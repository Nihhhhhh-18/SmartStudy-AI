"""
tests/test_llm_service.py — Unit tests for llm_service helper functions.
"""

import os
from unittest.mock import patch, MagicMock
from src.llm_service import (
    _extract_text_content,
    get_llm_info,
    _search_environ,
    _search_streamlit_secrets,
    _get_env,
    is_api_key_configured,
)


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


def test_search_environ_exact_and_case_insensitive():
    with patch.dict(os.environ, {"MY_TEST_KEY": "secret123", "lower_key": "secret456"}, clear=False):
        assert _search_environ(["MY_TEST_KEY"]) == "secret123"
        assert _search_environ(["LOWER_KEY"]) == "secret456"
        assert _search_environ(["NON_EXISTENT"]) is None


def test_get_env_aliases():
    # Test that GOOGLE_API_KEY is found when looking up LLM_API_KEY
    with patch.dict(os.environ, {"GOOGLE_API_KEY": "google-test-key"}, clear=True):
        assert _get_env("LLM_API_KEY") == "google-test-key"
        assert is_api_key_configured() is True


def test_search_streamlit_secrets_nested():
    mock_secrets = {
        "google": {
            "api_key": "nested-secret-key"
        }
    }
    with patch("src.llm_service.st", create=True) as mock_st:
        mock_st.secrets = mock_secrets
        # Should find key inside nested dict
        val = _search_streamlit_secrets(["LLM_API_KEY", "api_key"])
        assert val == "nested-secret-key"
