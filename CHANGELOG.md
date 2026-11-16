# 📝 Changelog — SmartStudy AI
All notable changes and development progress since **Milestone 1** (11 October 2026) are documented in this file.

---

## [Milestone 2] — 2026-11-16

### Added
- **Automated 10-Point Structural Output Validator (`src/output_validator.py`):**
  - Enforces presence of exactly 3 required sections (`Summary`, `Key Terms and Definitions`, `Practice Questions`).
  - Verifies section ordering and flags illegal extra top-level sections (e.g., separate answer keys).
  - Validates exact question count (5 questions) and sequential numbering (1 through 5).
  - Checks inline answer labeling for each practice question.
- **Production Prompt V3 (`prompts/improved_prompt_v2.txt`):**
  - Incorporated strict negative grounding constraints.
  - Added deterministic fallback sentence for undefined terms: *"The supplied notes do not define this term in detail."*
  - Enforced Bloom's taxonomy pedagogical order: Multiple Choice (with distractors), Short Answer, Fill-in-the-Blank, Scenario Application, True/False with correction.
  - Added silent self-verification directive to prevent meta-commentary leakage.
- **Side-by-Side Prompt Comparison Engine (`app.py`):**
  - Implemented concurrent dual-prompt generation using Python's `ThreadPoolExecutor`.
  - Added side-by-side output view with automated structural comparison tables.
- **Automated Test Suite (`tests/`):**
  - 56 comprehensive unit tests covering document loaders, prompt managers, LLM content extractors, and regex validators.
- **PDF Export & Reporting Pipeline (`generate_milestone_pdfs.py`):**
  - Direct generation of compliant Milestone 2 submission PDF (`M2_TeamID_SmartStudyAI.pdf`) and Technical Report (`TeamName_TechnicalReport.pdf`).
- **Demo Reel Narration Guide (`reel_script_115_seconds.md`):**
  - Word-for-word 115-second script matching guideline requirements.

### Changed
- **Modular Refactoring (`src/`):**
  - Decoupled application logic into distinct modules: `document_loader.py`, `llm_service.py`, `prompt_manager.py`, and `output_validator.py`.
- **Document Ingestion (`src/document_loader.py`):**
  - Added dual UTF-8 / Latin-1 encoding fallback to prevent crashes on non-standard text files.
  - Enhanced PyMuPDF PDF parser to detect and gracefully handle scanned/image-only PDFs.
- **UI Enhancements (`app.py`):**
  - Styled interface with modern typography, validation badges (green pass / amber warning), and direct Markdown download button with reproducible metadata.

### Fixed
- Fixed `PyMuPDF` module import compatibility (`import pymupdf` with legacy `fitz` fallback).
- Fixed markdown table rendering failures in earlier prompt iterations by standardizing on bullet lists.
- Eliminated hallucinated definitions for passingly mentioned concepts (*pruning*, *dropout*).

---

## [Milestone 1] — 2026-10-11

### Added
- Initial project formulation for Problem Statement C2 (Lecture Notes to Study Pack).
- Baseline prompt prototype (`baseline_prompt_v1.txt`).
- Basic lecture notes extraction script.
- Sample dataset (`sample_lecture_notes.txt`).
- Initial evaluation rubric and baseline output records.

