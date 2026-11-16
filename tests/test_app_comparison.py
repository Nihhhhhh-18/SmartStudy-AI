"""
tests/test_app_comparison.py — Unit tests for application comparison and selection logic.

These tests run without an API key using mocked generation results.
"""

from unittest.mock import patch
from src.prompt_manager import list_prompt_versions, load_prompt_template
from src.output_validator import analyze_output, validate_output
from app import _run_generation

SAMPLE_NOTES = """
# Machine Learning: Overfitting
Overfitting occurs when a model learns training data too closely.
Regularization reduces overfitting by discouraging excessive complexity.
"""

MOCK_V1_OUTPUT = """
## 1. Summary
Overfitting happens when a model learns data too closely.

## 2. Key Terms and Definitions
- Overfitting: Learns data too closely.
- Regularization: Reduces overfitting.

## 3. Practice Questions
### Question 1
What is overfitting?
Answer: Learns noise.

### Question 2
What is regularization?
Answer: Reduces complexity.

### Question 3
___ reduces complexity.
Answer: Regularization

### Question 4
In this scenario...
Answer: Apply regularization.

### Question 5
True or False: Regularization helps.
Answer: True.
"""

MOCK_V2_OUTPUT = """
## 1. Summary
Overfitting occurs when a model fits training data too closely. Regularization reduces complexity.

## 2. Key Terms and Definitions
- Overfitting: Learns training data too closely.
- Regularization: Discourages excessive model complexity.

## 3. Practice Questions
### Question 1 (Multiple Choice)
What is overfitting?
A) Good B) Bad
Answer: B

### Question 2 (Short Answer)
Define regularization.
Answer: Discourages complexity.

### Question 3 (Fill-in-the-Blank)
___ reduces overfitting.
Answer: Regularization

### Question 4 (Scenario-Based)
A model has high complexity.
Answer: Use regularization.

### Question 5 (True/False)
Regularization increases complexity.
Answer: False. It discourages excessive complexity.
"""


def test_prompt_versions_separately_selectable():
    versions = list_prompt_versions()
    assert len(versions) >= 2
    assert "V1 — Baseline" in versions
    assert any("V2" in v for v in versions)


def test_comparison_supplies_identical_notes_and_keeps_templates_distinct():
    v1_tpl = load_prompt_template("V1 — Baseline")
    versions = list_prompt_versions()
    v2_name = [v for v in versions if "V2" in v][0]
    v2_tpl = load_prompt_template(v2_name)

    v1_formatted = v1_tpl.format(lecture_notes=SAMPLE_NOTES)
    v2_formatted = v2_tpl.format(lecture_notes=SAMPLE_NOTES)

    # Identical notes are injected
    assert SAMPLE_NOTES in v1_formatted
    assert SAMPLE_NOTES in v2_formatted
    # Templates remain strictly distinct
    assert v1_formatted != v2_formatted


def test_run_generation_associates_correct_version_and_analysis():
    with patch("app.generate_study_pack", return_value=MOCK_V1_OUTPUT):
        out, warnings, prompt_file, analysis = _run_generation(SAMPLE_NOTES, "V1 — Baseline")
        assert out == MOCK_V1_OUTPUT
        assert prompt_file == "baseline_prompt_v1.txt"
        assert isinstance(warnings, list)
        assert isinstance(analysis, dict)
        assert analysis["question_count"] == 5
        assert analysis["passed_all_structural_checks"] is True


def test_validation_is_run_separately_on_each_output():
    analysis_v1 = analyze_output(MOCK_V1_OUTPUT)
    analysis_v2 = analyze_output(MOCK_V2_OUTPUT)

    assert analysis_v1["question_count"] == 5
    assert analysis_v2["question_count"] == 5


def test_structural_pass_does_not_imply_factual_correctness():
    # A structurally valid output with complete falsehoods
    factually_wrong_output = """
    ## 1. Summary
    The Earth is flat and the Moon is made of green cheese.

    ## 2. Key Terms and Definitions
    - **Flat Earth**: The Earth has edges.
    - **Moon Cheese**: The lunar surface is dairy.

    ## 3. Practice Questions
    ### Question 1
    What is the Moon made of?
    Answer: Green cheese.
    ### Question 2
    Is Earth flat?
    Answer: Yes.
    ### Question 3
    ___ is on the moon.
    Answer: Cheese
    ### Question 4
    Scenario: ...
    Answer: Flat
    ### Question 5
    True or false: Moon is cheese.
    Answer: True.
    """
    analysis = analyze_output(factually_wrong_output)
    # It passes structural validation because it has 3 sections and 5 answered questions
    assert analysis["passed_all_structural_checks"] is True
    # But as documented, structural validation does NOT verify factual correctness
    # This proves structural checking must be distinct from factual evaluation
