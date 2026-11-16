"""
output_validator.py — Validate the structure of an LLM-generated study pack.

These checks verify **structure**, not factual correctness.
The model's output may still contain factual errors, unsupported claims, or
improper definitions even if all structural checks pass.

Structural checks performed:
1. Whether the Summary section exists.
2. Whether the Key Terms and Definitions section exists.
3. Whether the Practice Questions section exists.
4. Whether these sections appear in the expected order (Summary -> Key Terms -> Practice Questions).
5. Whether unexpected additional top-level sections exist.
6. Whether exactly five practice questions are present.
7. Whether questions are numbered sequentially from 1 to 5.
8. Whether question numbering is duplicated, missing, or malformed.
9. Whether every question has a clearly labelled answer.
10. Whether any required section is empty.
"""

import re
from typing import Any

# ═══════════════════════════════════════════════════════════════════════════
# Grounding review checklist for manual evaluation
# ═══════════════════════════════════════════════════════════════════════════
MANUAL_GROUNDING_CHECKLIST = [
    {
        "id": "E1",
        "name": "Summary coverage",
        "description": "Summary covers all major concepts and relationships from the lecture notes.",
    },
    {
        "id": "E2",
        "name": "Factual grounding",
        "description": "No outside facts, unsupported claims, or invented examples introduced.",
    },
    {
        "id": "E3",
        "name": "Technical-term compliance",
        "description": "Listed terms appear explicitly in the notes without extraneous additions.",
    },
    {
        "id": "E4",
        "name": "Definition accuracy",
        "description": "Definitions are accurate to the notes, or use the exact fallback when undefined.",
    },
    {
        "id": "E5",
        "name": "Exactly five questions",
        "description": "Exactly five distinct practice questions are generated.",
    },
    {
        "id": "E6",
        "name": "Answers present and correct",
        "description": "Every question includes a correct, clearly labelled answer supported by the notes.",
    },
    {
        "id": "E7",
        "name": "Question-type diversity and compliance",
        "description": "Mixed question types are used in the required order and test genuine comprehension.",
    },
    {
        "id": "E8",
        "name": "Formatting and instruction-following",
        "description": "Follows section structure, avoids tables, and observes all negative constraints.",
    },
]


def _coerce_str(text: Any) -> str:
    """Safely convert any input (including lists of content) into a plain string."""
    if text is None:
        return ""
    if isinstance(text, str):
        return text
    if isinstance(text, list):
        return "\n".join(str(item) for item in text)
    return str(text)


def _has_section(text: str, heading: str) -> bool:
    """
    Return True if *text* contains a Markdown heading matching *heading*
    (case-insensitive, with or without ##, numbering, or bold).
    """
    pattern = (
        rf"(?:^|\n)\s*(?:[-*•]\s*)?(?:#+\s*)?(?:\d+\.\s*)?"
        rf"(?:\*{1,2}|_{1,2})?"
        rf"{re.escape(heading)}"
    )
    return bool(re.search(pattern, text, re.IGNORECASE))


def check_sections(text: str) -> dict[str, bool]:
    """
    Check whether the three required sections appear in *text*.

    Returns a dict mapping section name -> found (True/False).
    """
    text = _coerce_str(text)
    return {
        "Summary": _has_section(text, "Summary"),
        "Key Terms": (
            _has_section(text, "Key Terms")
            or _has_section(text, "Key Terms and Definitions")
        ),
        "Practice Questions": (
            _has_section(text, "Practice Questions")
            or _has_section(text, "Questions")
        ),
    }


def _extract_practice_questions_content(text: str) -> tuple[str, int]:
    """
    Extract only the content inside the Practice Questions section.

    Returns (pq_content, start_offset). If the section is not found,
    returns ("", -1).
    """
    pq_match = re.search(
        r"(?:^|\n)\s*(?:#+\s*(?:\d+\.\s*)?|(?:\*\*))(?:Practice\s+)?Questions\b",
        text,
        re.IGNORECASE,
    )
    if not pq_match:
        return "", -1

    after_pq = text[pq_match.end():]

    # Stop at the next top-level heading (## ...) if one exists
    next_top_level = re.search(r"(?:^|\n)##\s+", after_pq)
    if next_top_level:
        pq_content = after_pq[:next_top_level.start()]
    else:
        pq_content = after_pq

    return pq_content, pq_match.start()


def _extract_question_matches(target_text: str) -> list[re.Match]:
    """
    Extract question match objects from target text.
    Filters out repeated question headers/titles within the same question block
    (e.g., '### Question 1' immediately followed by 'Question 1: What is...').
    """
    raw_matches = list(re.finditer(
        r"(?:^|\n)\s*(?:[-*•]\s*)?(?:#+\s*)?(?:\*{1,2}|_{1,2})?(?:Question|Q)\s*(\d+)",
        target_text,
        re.IGNORECASE,
    ))

    if raw_matches:
        filtered_matches: list[re.Match] = []
        for match in raw_matches:
            if not filtered_matches:
                filtered_matches.append(match)
            else:
                prev = filtered_matches[-1]
                between = target_text[prev.end():match.start()]
                # If the same number appears without an Answer: in between, it is a repeated header/title
                if match.group(1) == prev.group(1) and not re.search(r"(?:Answer|Ans)\s*:", between, re.IGNORECASE):
                    continue
                filtered_matches.append(match)
        return filtered_matches

    # Fallback to numbered list items (e.g. "1.", "2.")
    numbered = list(re.finditer(
        r"(?:^|\n)\s*(?:[-*•]\s*)?(?:#+\s*)?(?:\*{1,2}|_{1,2})?(\d+)[\.\)]\s",
        target_text,
    ))
    return numbered


def count_questions(text: str) -> int:
    """
    Count the number of practice questions in the output.

    Restricts search strictly to the Practice Questions section so that
    numbered lists in the Summary or Key Terms are not counted as questions.
    """
    text = _coerce_str(text)
    pq_content, _ = _extract_practice_questions_content(text)
    target_text = pq_content if pq_content else text

    matches = _extract_question_matches(target_text)
    return len(matches)


def analyze_output(text: object) -> dict[str, Any]:
    """
    Run detailed structural analysis on the study pack text.

    Returns a comprehensive dict with section metrics, question sequence,
    answer labels, unexpected top-level sections, and warning messages.
    """
    raw_text = _coerce_str(text)
    warnings: list[str] = []

    if not raw_text.strip():
        return {
            "sections_found": {"Summary": False, "Key Terms": False, "Practice Questions": False},
            "sections_order_valid": False,
            "unexpected_sections": [],
            "empty_sections": [],
            "question_count": 0,
            "question_numbers": [],
            "sequential_numbering": False,
            "missing_question_numbers": [],
            "duplicate_question_numbers": [],
            "questions_missing_answers": [],
            "warnings": ["The model returned an empty response."],
            "passed_all_structural_checks": False,
        }

    # ── 1. Check required sections presence ───────────────────────────────
    summary_match = re.search(
        r"(?:^|\n)\s*(?:[-*•]\s*)?(?:#+\s*)?(?:\d+\.\s*)?(?:\*{1,2}|_{1,2})?Summary\b",
        raw_text,
        re.IGNORECASE,
    )
    key_terms_match = re.search(
        r"(?:^|\n)\s*(?:[-*•]\s*)?(?:#+\s*)?(?:\d+\.\s*)?(?:\*{1,2}|_{1,2})?Key Terms(?:\s+and\s+Definitions)?\b",
        raw_text,
        re.IGNORECASE,
    )
    pq_match = re.search(
        r"(?:^|\n)\s*(?:[-*•]\s*)?(?:#+\s*)?(?:\d+\.\s*)?(?:\*{1,2}|_{1,2})?(?:Practice\s+)?Questions\b",
        raw_text,
        re.IGNORECASE,
    )

    sections_found = {
        "Summary": bool(summary_match),
        "Key Terms": bool(key_terms_match),
        "Practice Questions": bool(pq_match),
    }

    missing_sections = [s for s, found in sections_found.items() if not found]
    if missing_sections:
        warnings.append(
            f"The following expected section(s) were not found: {', '.join(missing_sections)}. "
            f"The output may be incomplete."
        )

    # ── 2. Check section order ────────────────────────────────────────────
    sections_order_valid = True
    if summary_match and key_terms_match and pq_match:
        pos_sum = summary_match.start()
        pos_terms = key_terms_match.start()
        pos_pq = pq_match.start()
        if not (pos_sum < pos_terms < pos_pq):
            sections_order_valid = False
            warnings.append(
                "Sections appear in an unexpected order. Expected: Summary, "
                "followed by Key Terms and Definitions, followed by Practice Questions."
            )

    # ── 3. Check for empty sections ───────────────────────────────────────
    empty_sections = []
    if summary_match and key_terms_match:
        summary_body = raw_text[summary_match.end():key_terms_match.start()].strip()
        if not summary_body:
            empty_sections.append("Summary")
    if key_terms_match and pq_match:
        terms_body = raw_text[key_terms_match.end():pq_match.start()].strip()
        if not terms_body:
            empty_sections.append("Key Terms and Definitions")
    if pq_match:
        pq_body = raw_text[pq_match.end():].strip()
        if not pq_body:
            empty_sections.append("Practice Questions")

    for sec in empty_sections:
        warnings.append(f"The '{sec}' section appears to be empty.")

    # ── 4. Check for unexpected top-level sections ─────────────────────────
    unexpected_sections = []
    level2_matches = re.findall(r"(?:^|\n)##\s+(.+)", raw_text)
    known_keywords = ("summary", "key term", "question", "study pack", "smartstudy")
    for heading in level2_matches:
        h_clean = heading.strip()
        if not any(k in h_clean.lower() for k in known_keywords):
            unexpected_sections.append(h_clean)

    if unexpected_sections:
        warnings.append(
            f"Unexpected additional top-level section(s) found: {', '.join(unexpected_sections)}. "
            f"The study pack should contain only Summary, Key Terms, and Practice Questions."
        )

    # ── 5. Question extraction and numbering checks ───────────────────────
    pq_content, _ = _extract_practice_questions_content(raw_text)
    target_q_text = pq_content if pq_content else raw_text

    # Match questions in target section using robust extraction
    q_matches = _extract_question_matches(target_q_text)

    question_numbers: list[int] = []
    for m in q_matches:
        try:
            question_numbers.append(int(m.group(1)))
        except ValueError:
            pass

    question_count = len(question_numbers)

    # Question count check
    if question_count == 0:
        warnings.append(
            "Could not identify any practice questions. "
            "The output may be missing the Practice Questions section."
        )
    elif question_count != 5:
        warnings.append(
            f"Expected exactly 5 practice questions but detected {question_count}. "
            f"Please review the output."
        )

    # Sequential numbering check
    duplicate_numbers = [n for n in set(question_numbers) if question_numbers.count(n) > 1]
    missing_numbers = [n for n in range(1, 6) if n not in question_numbers]
    sequential_numbering = (question_numbers == [1, 2, 3, 4, 5])

    if question_count == 5 and not sequential_numbering:
        if duplicate_numbers:
            warnings.append(
                f"Duplicate question numbering detected: Question {', '.join(str(d) for d in duplicate_numbers)}."
            )
        if missing_numbers:
            warnings.append(
                f"Missing question numbering detected: Question {', '.join(str(m) for m in missing_numbers)}."
            )
        if not duplicate_numbers and not missing_numbers:
            warnings.append(
                f"Questions are not numbered sequentially from 1 to 5: found {question_numbers}."
            )

    # ── 6. Check for clearly labelled answers ─────────────────────────────
    questions_missing_answers: list[int] = []
    if q_matches:
        for idx in range(len(q_matches)):
            start_pos = q_matches[idx].start()
            end_pos = q_matches[idx + 1].start() if idx + 1 < len(q_matches) else len(target_q_text)
            chunk = target_q_text[start_pos:end_pos]
            has_ans = bool(re.search(
                r"(?:^|\n|\s)(?:\*{1,2}|_{1,2})?(?:Answer|Ans)\s*(?:\*{1,2}|_{1,2})?:",
                chunk,
                re.IGNORECASE,
            ))
            if not has_ans:
                q_num = question_numbers[idx] if idx < len(question_numbers) else idx + 1
                questions_missing_answers.append(q_num)

    if questions_missing_answers:
        warnings.append(
            f"The following question(s) do not have a clearly labelled 'Answer:': "
            f"Question {', '.join(str(q) for q in questions_missing_answers)}."
        )

    passed_all = (len(warnings) == 0)

    return {
        "sections_found": sections_found,
        "sections_order_valid": sections_order_valid,
        "unexpected_sections": unexpected_sections,
        "empty_sections": empty_sections,
        "question_count": question_count,
        "question_numbers": question_numbers,
        "sequential_numbering": sequential_numbering,
        "missing_question_numbers": missing_numbers,
        "duplicate_question_numbers": duplicate_numbers,
        "questions_missing_answers": questions_missing_answers,
        "warnings": warnings,
        "passed_all_structural_checks": passed_all,
    }


def validate_output(text: object) -> list[str]:
    """
    Run all structural checks and return a list of warning messages.

    An empty list means all checks passed.

    **Important**: Passing these checks verifies **structure only**.
    It does NOT guarantee factual correctness, grounding, or definition
    accuracy.
    """
    analysis = analyze_output(text)
    return analysis["warnings"]
