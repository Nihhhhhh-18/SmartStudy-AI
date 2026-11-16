"""
llm_service.py — Configure and invoke a LangChain LLM for SmartStudy AI.

Supports multiple providers through environment variables:
    LLM_PROVIDER   — "google"  (default) or "openai"
    LLM_MODEL      — model name, e.g. "gemini-3.8-flash" or "gpt-4o-mini"
    LLM_API_KEY    — the provider's API key (never hardcoded)

The module exposes a single ``generate_study_pack`` function that
accepts lecture-note text and a LangChain PromptTemplate, calls the
configured LLM, and returns the raw response string.
"""

import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate

# Load .env file so API keys are available
load_dotenv()

# ── Supported providers ─────────────────────────────────────────────────
_SUPPORTED_PROVIDERS = ("google", "openai")


class LLMConfigError(Exception):
    """Raised when the LLM cannot be configured (missing key, bad provider, etc.)."""


def _get_env(name: str, default: str | None = None) -> str:
    """Read an environment variable or Streamlit secret, stripping whitespace."""
    value = os.getenv(name)
    if value is None:
        try:
            import streamlit as st
            if hasattr(st, "secrets") and name in st.secrets:
                value = str(st.secrets[name])
        except Exception:
            pass
    if value is None:
        value = default
    if value is not None:
        value = value.strip()
    return value  # type: ignore[return-value]


def _build_llm():
    """
    Build and return a LangChain chat-model instance based on env vars.

    Raises LLMConfigError with a helpful message if anything is missing.
    """
    provider = (_get_env("LLM_PROVIDER", "google") or "google").lower()
    model = _get_env("LLM_MODEL", "")
    api_key = _get_env("LLM_API_KEY", "")

    if not api_key:
        raise LLMConfigError(
            "LLM_API_KEY is not set. "
            "Create a .env file in the project root with:\n\n"
            "  LLM_PROVIDER=google\n"
            "  LLM_MODEL=gemini-3.8-flash\n"
            "  LLM_API_KEY=your-api-key-here\n\n"
            "See .env.example for a template."
        )

    if provider not in _SUPPORTED_PROVIDERS:
        raise LLMConfigError(
            f"Unsupported LLM_PROVIDER '{provider}'. "
            f"Supported providers: {', '.join(_SUPPORTED_PROVIDERS)}."
        )

    # ── Google (Gemini) ─────────────────────────────────────────────────
    if provider == "google":
        if not model:
            model = "gemini-3.5-flash"
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
        except ImportError as exc:
            raise LLMConfigError(
                "langchain-google-genai is not installed. "
                "Run: pip install langchain-google-genai"
            ) from exc

        return ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
            temperature=0.3,
            convert_system_message_to_human=True,
        )

    # ── OpenAI ──────────────────────────────────────────────────────────
    if provider == "openai":
        if not model:
            model = "gpt-4o-mini"
        try:
            from langchain_openai import ChatOpenAI
        except ImportError as exc:
            raise LLMConfigError(
                "langchain-openai is not installed. "
                "Run: pip install langchain-openai"
            ) from exc

        return ChatOpenAI(
            model=model,
            api_key=api_key,
            temperature=0.3,
        )

    # Should never reach here because of the provider check above
    raise LLMConfigError(f"Provider '{provider}' is not implemented.")


def get_llm_info() -> dict[str, str]:
    """
    Return a dict with the current provider and model name for display.
    Does not expose the API key.
    """
    provider = (_get_env("LLM_PROVIDER", "google") or "google").lower()
    model = _get_env("LLM_MODEL", "")
    if not model:
        model = "gemini-3.5-flash" if provider == "google" else "gpt-4o-mini"
    return {"provider": provider, "model": model}


def _extract_text_content(content: object) -> str:
    """
    Extract a plain string from AIMessage content, which may be a string
    or a list of content parts (dicts or objects) in newer LangChain versions.
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for part in content:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict):
                # Common shapes: {"type": "text", "text": "..."}
                if "text" in part:
                    parts.append(str(part["text"]))
                elif "content" in part:
                    parts.append(str(part["content"]))
                else:
                    parts.append(str(part))
            elif hasattr(part, "text"):
                parts.append(str(getattr(part, "text")))
            elif hasattr(part, "content"):
                parts.append(str(getattr(part, "content")))
            else:
                parts.append(str(part))
        return "".join(parts)
    return str(content) if content is not None else ""


def generate_study_pack(
    lecture_notes: str,
    prompt_template: PromptTemplate,
) -> str:
    """
    Generate a study pack by sending lecture notes through the prompt
    template to the configured LLM.

    Parameters
    ----------
    lecture_notes : str
        The extracted text from the user's uploaded notes.
    prompt_template : PromptTemplate
        A LangChain prompt template with a ``{lecture_notes}`` variable.

    Returns
    -------
    str
        The raw text response from the LLM.

    Raises
    ------
    LLMConfigError
        If the provider or API key is misconfigured.
    Exception
        Any exception raised by the provider SDK (network errors, etc.).
    """
    llm = _build_llm()

    # Build the LangChain chain: prompt | llm
    chain = prompt_template | llm

    # Invoke the chain with the lecture notes
    response = chain.invoke({"lecture_notes": lecture_notes})

    # LangChain chat models return an AIMessage; extract the text content safely
    if hasattr(response, "content"):
        return _extract_text_content(response.content)
    return _extract_text_content(response)
