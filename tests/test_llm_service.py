"""
tests/test_llm_service.py — Unit tests for llm_service helper functions.
"""

from src.llm_service import _extract_text_content, get_llm_info


def test_extract_text_from_string():
    assert _extract_text_content("Hello World") == "Hello World"


def test_extract_text_from_list_of_strings():
    assert _extract_text_content(["Hello ", "World"]) == "Hello World"


def test_extract_text_from_list_of_dicts():
    # Common shape from ChatGoogleGenerativeAI
    data = [
        {"type": "text", "text": "Generated summary: "},
        {"type": "text", "text": "Everything is fine."},
    ]
    assert _extract_text_content(data) == "Generated summary: Everything is fine."


def test_extract_text_from_none():
    assert _extract_text_content(None) == ""


def test_get_llm_info():
    info = get_llm_info()
    assert "provider" in info
    assert "model" in info
