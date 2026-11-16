"""
prompt_manager.py — Load and manage prompt templates for SmartStudy AI.

Prompt templates live in the ``prompts/`` directory as plain-text files
with a ``{lecture_notes}`` placeholder.  This module reads them and
exposes them as LangChain PromptTemplate objects.
"""

from pathlib import Path

from langchain_core.prompts import PromptTemplate

# ── Locate the prompts directory relative to this file ──────────────────
# Project layout:  SmartStudy-AI/src/prompt_manager.py
#                  SmartStudy-AI/prompts/*.txt
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = _PROJECT_ROOT / "prompts"

# ── Registry of known prompt versions ───────────────────────────────────
PROMPT_VERSIONS: dict[str, str] = {
    "V1 — Baseline": "baseline_prompt_v1.txt",
    "V2 — Improved (recommended)": "improved_prompt_v2.txt",
}

# Default version key
DEFAULT_VERSION = "V2 — Improved (recommended)"


def list_prompt_versions() -> list[str]:
    """Return the display names of all registered prompt versions."""
    return list(PROMPT_VERSIONS.keys())


def load_prompt_template(version_name: str) -> PromptTemplate:
    """
    Load a prompt template by its display name.

    Parameters
    ----------
    version_name : str
        One of the keys in ``PROMPT_VERSIONS``.

    Returns
    -------
    langchain_core.prompts.PromptTemplate
        A template with a single input variable ``lecture_notes``.

    Raises
    ------
    FileNotFoundError
        If the template file does not exist on disk.
    ValueError
        If the version name is not recognised.
    """
    filename = PROMPT_VERSIONS.get(version_name)
    if filename is None:
        raise ValueError(
            f"Unknown prompt version '{version_name}'. "
            f"Available versions: {list_prompt_versions()}"
        )

    filepath = PROMPTS_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Prompt file not found: {filepath}")

    raw_template = filepath.read_text(encoding="utf-8")

    # LangChain PromptTemplate expects Python-style {variable} placeholders.
    # Our text files already use {lecture_notes}.
    return PromptTemplate(
        input_variables=["lecture_notes"],
        template=raw_template,
    )


def get_prompt_filename(version_name: str) -> str:
    """Return the filename (not the full path) for a given version name."""
    filename = PROMPT_VERSIONS.get(version_name)
    if filename is None:
        raise ValueError(f"Unknown prompt version '{version_name}'.")
    return filename
