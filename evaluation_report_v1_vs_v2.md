# SmartStudy AI — Prompt Evaluation Report: V1 (Revised Baseline) vs. V2 (Improved)

**Date of Evaluation:** October 24, 2026  
**Evaluator:** SmartStudy AI Evaluation Engine & Senior AI Application Engineer  
**Model / Provider:** `google/gemini-3.5-flash` (temperature=0.3)  
**Input Document:** `sample_lecture_notes.txt` (Machine Learning: Overfitting and Regularization)  
**Historical Note:** Earlier preliminary evaluation runs are preserved in `evaluation_v1.txt` and `evaluation_v2.txt`. This report documents the head-to-head empirical experiment comparing the simplified baseline (`prompts/baseline_prompt_v1.txt`) with the improved prompt (`prompts/improved_prompt_v2.txt`).

---

## 1. Automated Structural Validation Results

Both outputs were evaluated using the enhanced 10-point structural validator (`src/output_validator.py`):

| Structural Check | V1 — Baseline (`prompts/baseline_prompt_v1.txt`) | V2 — Improved (`prompts/improved_prompt_v2.txt`) |
| :--- | :---: | :---: |
| **All 3 Required Sections Present** | ✅ Pass (`Summary`, `Key Terms`, `Practice Questions`) | ✅ Pass (`Summary`, `Key Terms`, `Practice Questions`) |
| **Section Order (1 → 2 → 3)** | ✅ Pass | ✅ Pass |
| **No Unexpected Top-Level Sections** | ❌ **Fail** (Detected unexpected `## 4. Answer Key`) | ✅ **Pass** (Exactly 3 top-level sections) |
| **Empty Section Detection** | ✅ Pass (All sections populated) | ✅ Pass (All sections populated) |
| **Exactly 5 Questions Detected** | ✅ Pass (5 questions detected) | ✅ Pass (5 questions detected) |
| **Sequential Question Numbering** | ✅ Pass (`[1, 2, 3, 4, 5]`) | ✅ Pass (`[1, 2, 3, 4, 5]`) |
| **Answers Labelled per Question** | ❌ **Fail** (Answers separated into Section 4) | ✅ **Pass** (Every question has inline `**Answer:**`) |
| **Overall Structural Status** | ⚠️ **2 Warning(s)** | ✅ **All Structural Checks Passed** |

---

## 2. Standardized 8-Point Manual Grounding & Quality Rubric

Scoring: `1 = Pass`, `0 = Fail`.

| ID | Criterion | V1 (Baseline) | V2 (Improved) | Evidence & Comparative Analysis |
|---|---|:---:|:---:|---|
| **E1** | **Summary coverage** | **1** | **1** | **V1:** Covered all 6 concepts (overfitting, underfitting, generalization, regularization, cross-validation, other methods).<br>**V2:** Covered all 6 concepts concisely with explicit bullet points suitable for intermediate undergraduates. |
| **E2** | **Factual grounding** | **0** | **1** | **V1 (Fail):** Introduced external pretraining facts not in the notes for Pruning (*"remove sections of the tree that provide little power in classifying instances"*) and Dropout (*"randomly setting a fraction of input units to zero during training"*).<br>**V2 (Pass):** 100% grounded. Introduced zero outside mechanisms. |
| **E3** | **Technical-term compliance** | **1** | **1** | **V1:** Extracted valid terms from the notes.<br>**V2:** Extracted exactly the technical terms from the notes without extraneous additions. |
| **E4** | **Definition accuracy** | **0** | **1** | **V1 (Fail):** Inferred external definitions for undefined terms instead of noting source limitations.<br>**V2 (Pass):** For terms without explicit definitions in the notes (*Decision Trees, Dropout, Neural Networks, Pruning*), V2 strictly adhered to the canonical fallback sentence: *"The supplied notes do not define this term in detail."* |
| **E5** | **Exactly five questions** | **1** | **1** | **V1:** Exactly 5 questions were generated.<br>**V2:** Exactly 5 questions were generated sequentially (Questions 1 through 5). |
| **E6** | **Answers present and correct** | **1** | **1** | **V1:** Answers present in Section 4; factually aligned with notes.<br>**V2:** Answers placed directly beneath each question with clear `**Answer:**` labels and concise supporting explanations. |
| **E7** | **Question-type diversity and compliance** | **0** | **1** | **V1 (Fail):** All 5 questions were generic open recall / short-answer questions. Zero multiple choice, zero fill-in-the-blank, zero scenario-based, zero true/false.<br>**V2 (Pass):** 100% compliant with the required pedagogical order:<br>1. Multiple Choice (with distractors)<br>2. Short Answer<br>3. Fill-in-the-Blank<br>4. Scenario-Based Application<br>5. True/False (with source-supported correction for False statement). |
| **E8** | **Formatting and instruction-following** | **0** | **1** | **V1 (Fail):** Created an unexpected 4th top-level section (`## 4. Answer Key`), separating questions from their answers.<br>**V2 (Pass):** Followed all negative constraints: exactly 3 sections, no tables, no conclusion, silent internal verification. |
| **TOTAL** | **Final Score** | **4 / 8 (50.0%)** | **8 / 8 (100.0%)** | **V2 demonstrates clear, measurable improvement (+50.0%)** |

---

## 3. Detailed Error Analysis

### Where V1 (Baseline Prompt) Fell Short
1. **Hallucination of External Knowledge (E2 & E4):**
   When asked to explain key terms, the baseline prompt did not restrict the model to *only* what was defined in the notes. As a consequence, the model hallucinated technical definitions for *pruning* and *dropout* drawn from general pretraining data rather than the provided lecture text.
2. **Pedagogical Homogeneity (E7):**
   Without explicit type constraints, the model defaulted to 5 homogeneous short-answer recall questions, missing opportunities to test application, discrimination, and recall.
3. **Structural Segregation (E8):**
   The model placed all answers into a separate top-level `## 4. Answer Key` section, violating the 3-section target and making self-study less cohesive.

### Why V2 (Improved Prompt) Succeeded
1. **Deterministic Fallback Sentence:**
   By prescribing `"The supplied notes do not define this term in detail."`, V2 turned an ambiguous hallucination hazard into a deterministic, reliable, source-grounded response.
2. **Bloom's Taxonomy / Multi-Tiered Assessment:**
   By requiring Multiple Choice, Short Answer, Fill-in-the-Blank, Scenario-Based, and True/False with corrections, V2 ensures comprehensive evaluation across recognition, recall, and real-world application.
3. **Clean Structural Conformance:**
   The negative formatting constraints and silent self-verification ensured exactly 3 top-level sections without markdown tables or stray conclusion headers.

---

## 4. Artifact References
- **V1 Generated Output:** `generated_v1_output.txt`
- **V2 Generated Output:** `generated_v2_output.txt`
- **Historical Reports:** `evaluation_v1.txt`, `evaluation_v2.txt`
