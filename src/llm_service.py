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

try:
    import streamlit as st
except ImportError:
    st = None  # type: ignore

# Load .env file so API keys are available
load_dotenv()

# ── Supported providers ─────────────────────────────────────────────────
_SUPPORTED_PROVIDERS = ("google", "openai")


class LLMConfigError(Exception):
    """Raised when the LLM cannot be configured (missing key, bad provider, etc.)."""


def _search_streamlit_secrets(candidate_keys: list[str]) -> str | None:
    """Safely search st.secrets for any of candidate_keys (case-insensitive, deep)."""
    try:
        if st is None or not hasattr(st, "secrets") or not st.secrets:
            return None

        lower_candidates = {k.lower() for k in candidate_keys}

        def _walk(item):
            # Check direct keys if dict-like
            if hasattr(item, "keys"):
                for k in list(item.keys()):
                    if str(k).lower() in lower_candidates:
                        val = item[k]
                        if val is not None and str(val).strip():
                            return str(val).strip()
                for k in list(item.keys()):
                    val = item[k]
                    res = _walk(val)
                    if res:
                        return res
            elif isinstance(item, (list, tuple)):
                for elem in item:
                    res = _walk(elem)
                    if res:
                        return res
            return None

        return _walk(st.secrets)
    except Exception:
        return None


def _search_environ(candidate_keys: list[str]) -> str | None:
    """Search os.environ for candidate_keys (exact match first, then case-insensitive)."""
    # 1. Exact match
    for key in candidate_keys:
        val = os.getenv(key)
        if val is not None and val.strip():
            return val.strip()

    # 2. Case-insensitive match
    lower_candidates = {k.lower() for k in candidate_keys}
    for env_k, env_v in os.environ.items():
        if env_k.lower() in lower_candidates and env_v and env_v.strip():
            return env_v.strip()

    return None


def _get_env(name: str, default: str | None = None) -> str:
    """
    Read a configuration value from os.environ or Streamlit secrets.
    Supports case-insensitivity, deep nested sections, and provider aliases.
    """
    aliases_map: dict[str, list[str]] = {
        "LLM_API_KEY": [
            "LLM_API_KEY",
            "GOOGLE_API_KEY",
            "GEMINI_API_KEY",
            "OPENAI_API_KEY",
            "API_KEY",
            "KEY",
        ],
        "LLM_PROVIDER": [
            "LLM_PROVIDER",
            "PROVIDER",
        ],
        "LLM_MODEL": [
            "LLM_MODEL",
            "MODEL",
        ],
    }

    candidates = aliases_map.get(name, [name])

    # 1. Check os.environ
    env_val = _search_environ(candidates)
    if env_val:
        return env_val

    # 2. Check streamlit.secrets (top-level and nested sections)
    sec_val = _search_streamlit_secrets(candidates)
    if sec_val:
        return sec_val

    return default.strip() if default is not None else ""


def is_api_key_configured() -> bool:
    """Return True if an LLM API key can be located in env or secrets."""
    key = _get_env("LLM_API_KEY", "")
    return bool(key)


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
            "LLM_API_KEY is not set.\n\n"
            "If deployed on Streamlit Cloud:\n"
            "1. Go to your App Settings → Secrets.\n"
            "2. Add the following (TOML format with quotes):\n\n"
            "     LLM_PROVIDER = \"google\"\n"
            "     LLM_MODEL = \"gemini-2.5-flash\"\n"
            "     LLM_API_KEY = \"your-api-key-here\"\n\n"
            "3. Click Save and reboot the app.\n\n"
            "Alternatively, paste your API key directly into the sidebar override field in the app.\n\n"
            "For local runs, create a .env file with LLM_API_KEY=your-api-key-here."
        )

    if provider not in _SUPPORTED_PROVIDERS:
        raise LLMConfigError(
            f"Unsupported LLM_PROVIDER '{provider}'. "
            f"Supported providers: {', '.join(_SUPPORTED_PROVIDERS)}."
        )

    # ── Google (Gemini) ─────────────────────────────────────────────────
    if provider == "google":
        if not model:
            model = "gemini-2.5-flash"
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
        model = "gemini-2.5-flash" if provider == "google" else "gpt-4o-mini"
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
