"""
tests/test_prompt_manager.py — Unit tests for the prompt manager module.

These tests run without an API key — they only test template loading
and variable substitution.
"""

import pytest

from src.prompt_manager import (
    list_prompt_versions,
    load_prompt_template,
    get_prompt_filename,
    PROMPTS_DIR,
    DEFAULT_VERSION,
)


class TestListPromptVersions:
    def test_returns_non_empty_list(self):
        versions = list_prompt_versions()
        assert len(versions) >= 2

    def test_contains_v1_and_v2(self):
        versions = list_prompt_versions()
        labels = " ".join(versions).lower()
        assert "v1" in labels
        assert "v2" in labels


class TestLoadPromptTemplate:
    def test_load_v1(self):
        versions = list_prompt_versions()
        tpl = load_prompt_template(versions[0])
        assert "lecture_notes" in tpl.input_variables

    def test_load_v2(self):
        tpl = load_prompt_template(DEFAULT_VERSION)
        assert "lecture_notes" in tpl.input_variables

    def test_template_contains_placeholder(self):
        tpl = load_prompt_template(DEFAULT_VERSION)
        # The raw template string should contain the placeholder
        assert "{lecture_notes}" in tpl.template

    def test_template_substitution(self):
        tpl = load_prompt_template(DEFAULT_VERSION)
        result = tpl.format(lecture_notes="Test notes about Python.")
        assert "Test notes about Python." in result
        assert "{lecture_notes}" not in result  # placeholder should be filled

    def test_templates_remain_distinct(self):
        v1_tpl = load_prompt_template("V1 — Baseline")
        v2_tpl = load_prompt_template(DEFAULT_VERSION)
        assert v1_tpl.template != v2_tpl.template
        # V1 is simplified baseline
        assert "Summarize the lecture notes" in v1_tpl.template
        # V2 contains detailed constraints
        assert "Strict source grounding" in v2_tpl.template or "Source Grounding" in v2_tpl.template
        assert "The supplied notes do not define this term in detail" in v2_tpl.template

    def test_missing_file_raises(self, monkeypatch, tmp_path):
        import src.prompt_manager as pm
        # Point PROMPTS_DIR to an empty temp dir
        monkeypatch.setattr(pm, "PROMPTS_DIR", tmp_path)
        with pytest.raises(FileNotFoundError, match="Prompt file not found"):
            pm.load_prompt_template("V1 — Baseline")


class TestGetPromptFilename:
    def test_known_version(self):
        fname = get_prompt_filename(DEFAULT_VERSION)
        assert fname.endswith(".txt")
        assert (PROMPTS_DIR / fname).exists()

    def test_unknown_version_raises(self):
        with pytest.raises(ValueError):
            get_prompt_filename("Fake version")

