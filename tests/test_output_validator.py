"""
tests/test_output_validator.py — Unit tests for the output validator module.

These tests run without an API key — they validate the structural
checking logic against synthetic outputs.
"""

import pytest

from src.output_validator import (
    MANUAL_GROUNDING_CHECKLIST,
    analyze_output,
    check_sections,
    count_questions,
    validate_output,
)

# ═══════════════════════════════════════════════════════════════════════════
# Sample outputs for testing
# ═══════════════════════════════════════════════════════════════════════════

GOOD_OUTPUT = """
## 1. Summary

Overfitting occurs when a model learns training data too closely.
Underfitting occurs when it fails to learn important patterns.

## 2. Key Terms and Definitions

- **Overfitting** — learning noise in the data.
- **Regularization** — reducing overfitting by discouraging complexity.

## 3. Practice Questions

### Question 1 — Multiple Choice
What is overfitting?
A) Low error
B) High training performance but poor generalization
Answer: B

### Question 2 — Short Answer
Define regularization.
Answer: It reduces overfitting by discouraging excessive complexity.

### Question 3 — Fill in the Blanks
Regularization discourages excessive model _____.
Answer: complexity

### Question 4 — Scenario-Based
A model performs well on training data but poorly on unseen data.
Answer: Overfitting.

### Question 5 — True or False
Regularization increases model complexity.
Answer: False. It discourages excessive complexity.
"""

OUTPUT_WITH_SUMMARY_NUMBERED_LIST = """
## 1. Summary

Here are three important techniques discussed:
1. Collecting representative data
2. Pruning decision trees
3. Using dropout in neural networks

## 2. Key Terms and Definitions

- **Overfitting** — fits training data too closely.
- **Dropout**: The supplied notes do not define this term in detail.

## 3. Practice Questions

### Question 1 (Multiple Choice)
What is overfitting?
Answer: A

### Question 2 (Short Answer)
What is underfitting?
Answer: Failure to learn key patterns.

### Question 3 (Fill-in-the-Blank)
___ evaluates a model.
Answer: Cross-validation

### Question 4 (Scenario-Based)
If a model memorizes data...
Answer: Apply regularization.

### Question 5 (True/False)
Is underfitting good?
Answer: False. It causes poor performance on both datasets.
"""

OUTPUT_WITH_ANSWER_NUMBERED_LIST = """
## 1. Summary
Good summary.

## 2. Key Terms and Definitions
- Term A: Def A

## 3. Practice Questions
### Question 1
Question 1 text?
Answer:
1. First reason
2. Second reason

### Question 2
Question 2 text?
Answer: Short answer.

### Question 3
Question 3 text?
Answer: Answer 3.

### Question 4
Question 4 text?
Answer: Answer 4.

### Question 5
Question 5 text?
Answer: Answer 5.
"""

OUT_OF_ORDER_OUTPUT = """
## 1. Practice Questions
### Question 1
Answer: A
### Question 2
Answer: B
### Question 3
Answer: C
### Question 4
Answer: D
### Question 5
Answer: E

## 2. Summary
Summary text.

## 3. Key Terms and Definitions
- Term: Def
"""

UNEXPECTED_SECTION_OUTPUT = """
## 1. Summary
Summary text.

## 2. Key Terms and Definitions
- Term: Def

## 3. Practice Questions
### Question 1
Answer: 1
### Question 2
Answer: 2
### Question 3
Answer: 3
### Question 4
Answer: 4
### Question 5
Answer: 5

## 4. Final Grounding Check
All checks passed.
"""

EMPTY_SECTION_OUTPUT = """
## 1. Summary

## 2. Key Terms and Definitions
- Term: Def

## 3. Practice Questions
### Question 1
Answer: 1
### Question 2
Answer: 2
### Question 3
Answer: 3
### Question 4
Answer: 4
### Question 5
Answer: 5
"""

MISSING_ANSWERS_OUTPUT = """
## 1. Summary
Summary text.

## 2. Key Terms and Definitions
- Term: Def

## 3. Practice Questions
### Question 1
What is X?
Answer: A

### Question 2
What is Y?
No answer provided here!

### Question 3
What is Z?
Answer: C

### Question 4
What is W?
Answer: D

### Question 5
What is V?
Answer: E
"""

NON_SEQUENTIAL_QUESTIONS_OUTPUT = """
## 1. Summary
Summary text.

## 2. Key Terms and Definitions
- Term: Def

## 3. Practice Questions
### Question 1
Answer: A
### Question 2
Answer: B
### Question 2
Answer: Duplicate 2
### Question 4
Answer: D
### Question 5
Answer: E
"""

MISSING_QUESTIONS_OUTPUT = """
## Summary
Some summary here.

## Key Terms and Definitions
- Term A
- Term B

## Practice Questions

### Question 1
What is A?
Answer: Something.

### Question 2
What is B?
Answer: Something else.
"""

NO_SECTIONS_OUTPUT = """
Here are some notes about machine learning.
Overfitting is bad. Regularization helps.
"""

EMPTY_OUTPUT = ""


# ═══════════════════════════════════════════════════════════════════════════
# check_sections
# ═══════════════════════════════════════════════════════════════════════════

class TestCheckSections:
    def test_all_sections_present(self):
        result = check_sections(GOOD_OUTPUT)
        assert all(result.values())

    def test_missing_sections(self):
        result = check_sections(NO_SECTIONS_OUTPUT)
        assert not all(result.values())


# ═══════════════════════════════════════════════════════════════════════════
# count_questions
# ═══════════════════════════════════════════════════════════════════════════

class TestCountQuestions:
    def test_five_questions(self):
        assert count_questions(GOOD_OUTPUT) == 5

    def test_two_questions(self):
        assert count_questions(MISSING_QUESTIONS_OUTPUT) == 2

    def test_no_questions(self):
        assert count_questions(NO_SECTIONS_OUTPUT) == 0

    def test_numbered_list_in_summary_not_counted_as_questions(self):
        # Summary has 1., 2., 3., and Practice Questions has 5 questions
        assert count_questions(OUTPUT_WITH_SUMMARY_NUMBERED_LIST) == 5

    def test_numbered_list_in_answer_not_counted_as_questions(self):
        # Answer to Q1 contains 1. and 2.
        assert count_questions(OUTPUT_WITH_ANSWER_NUMBERED_LIST) == 5


# ═══════════════════════════════════════════════════════════════════════════
# validate_output and analyze_output
# ═══════════════════════════════════════════════════════════════════════════

class TestValidateOutput:
    def test_good_output_no_warnings(self):
        warnings = validate_output(GOOD_OUTPUT)
        assert len(warnings) == 0

    def test_empty_output_warns(self):
        warnings = validate_output(EMPTY_OUTPUT)
        assert len(warnings) >= 1
        assert any("empty" in w.lower() for w in warnings)

    def test_missing_sections_warns(self):
        warnings = validate_output(NO_SECTIONS_OUTPUT)
        assert len(warnings) >= 1
        assert any("section" in w.lower() for w in warnings)

    def test_wrong_question_count_warns(self):
        warnings = validate_output(MISSING_QUESTIONS_OUTPUT)
        assert len(warnings) >= 1
        assert any("5" in w or "question" in w.lower() for w in warnings)

    def test_out_of_order_sections_warns(self):
        warnings = validate_output(OUT_OF_ORDER_OUTPUT)
        assert len(warnings) >= 1
        assert any("order" in w.lower() for w in warnings)

    def test_unexpected_top_level_section_warns(self):
        warnings = validate_output(UNEXPECTED_SECTION_OUTPUT)
        assert len(warnings) >= 1
        assert any("unexpected" in w.lower() for w in warnings)

    def test_empty_section_warns(self):
        warnings = validate_output(EMPTY_SECTION_OUTPUT)
        assert len(warnings) >= 1
        assert any("empty" in w.lower() for w in warnings)

    def test_missing_answer_warns(self):
        warnings = validate_output(MISSING_ANSWERS_OUTPUT)
        assert len(warnings) >= 1
        assert any("answer" in w.lower() for w in warnings)

    def test_duplicate_question_numbering_warns(self):
        warnings = validate_output(NON_SEQUENTIAL_QUESTIONS_OUTPUT)
        assert len(warnings) >= 1
        assert any("duplicate" in w.lower() or "sequential" in w.lower() for w in warnings)

    def test_none_input(self):
        warnings = validate_output(None)
        assert len(warnings) >= 1

    def test_list_input(self):
        warnings = validate_output([GOOD_OUTPUT])
        assert len(warnings) == 0

    def test_empty_list_input(self):
        warnings = validate_output([])
        assert len(warnings) >= 1
        assert any("empty" in w.lower() for w in warnings)

    def test_analyze_output_structure(self):
        analysis = analyze_output(GOOD_OUTPUT)
        assert analysis["passed_all_structural_checks"] is True
        assert analysis["question_count"] == 5
        assert analysis["sequential_numbering"] is True
        assert analysis["sections_order_valid"] is True
        assert len(analysis["warnings"]) == 0

    def test_manual_grounding_checklist_has_eight_criteria(self):
        assert len(MANUAL_GROUNDING_CHECKLIST) == 8
        ids = [c["id"] for c in MANUAL_GROUNDING_CHECKLIST]
        assert ids == ["E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8"]
