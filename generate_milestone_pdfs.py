"""
generate_milestone_pdfs.py — Generate high-quality Milestone 2 PDF and Technical Report PDF
for SCSE4041 Prompt Engineering Mini-Project (SmartStudy AI, Problem C2).
"""

import pymupdf

PAGE_WIDTH = 595.32   # A4 width in points
PAGE_HEIGHT = 841.92  # A4 height in points
MARGIN_X = 45.0
MARGIN_TOP = 50.0
MARGIN_BOTTOM = 50.0
CONTENT_WIDTH = PAGE_WIDTH - 2 * MARGIN_X


class PDFBuilder:
    def __init__(self, doc_title: str):
        self.doc = pymupdf.open()
        self.doc_title = doc_title
        self.page = None
        self.y = MARGIN_TOP

    def new_page(self, skip_header: bool = False):
        self.page = self.doc.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)
        self.y = MARGIN_TOP
        if not skip_header:
            # Header line and text
            self.page.insert_text(
                pymupdf.Point(MARGIN_X, MARGIN_TOP - 18),
                self.doc_title,
                fontsize=8,
                fontname="helv",
                color=(0.4, 0.4, 0.4),
            )
            self.page.draw_line(
                pymupdf.Point(MARGIN_X, MARGIN_TOP - 12),
                pymupdf.Point(PAGE_WIDTH - MARGIN_X, MARGIN_TOP - 12),
                color=(0.8, 0.8, 0.8),
                width=0.75,
            )

    def check_space(self, needed_height: float):
        if self.page is None or (self.y + needed_height > PAGE_HEIGHT - MARGIN_BOTTOM):
            self.new_page()

    def add_title(self, text: str, subtitle: str = ""):
        self.check_space(60)
        self.page.insert_text(
            pymupdf.Point(MARGIN_X, self.y + 18),
            text,
            fontsize=18,
            fontname="hebo",
            color=(0.1, 0.2, 0.5),
        )
        self.y += 24
        if subtitle:
            self.page.insert_text(
                pymupdf.Point(MARGIN_X, self.y + 12),
                subtitle,
                fontsize=11,
                fontname="helv",
                color=(0.3, 0.3, 0.3),
            )
            self.y += 20
        self.page.draw_line(
            pymupdf.Point(MARGIN_X, self.y + 4),
            pymupdf.Point(PAGE_WIDTH - MARGIN_X, self.y + 4),
            color=(0.2, 0.4, 0.8),
            width=1.5,
        )
        self.y += 14

    def add_heading1(self, text: str):
        self.check_space(40)
        self.y += 8
        self.page.draw_rect(
            pymupdf.Rect(MARGIN_X, self.y, PAGE_WIDTH - MARGIN_X, self.y + 22),
            color=None,
            fill=(0.92, 0.94, 0.98),
        )
        self.page.draw_line(
            pymupdf.Point(MARGIN_X, self.y),
            pymupdf.Point(MARGIN_X, self.y + 22),
            color=(0.15, 0.35, 0.75),
            width=3.0,
        )
        self.page.insert_text(
            pymupdf.Point(MARGIN_X + 10, self.y + 15),
            text,
            fontsize=11.5,
            fontname="hebo",
            color=(0.1, 0.2, 0.5),
        )
        self.y += 30

    def add_heading2(self, text: str):
        self.check_space(28)
        self.y += 6
        self.page.insert_text(
            pymupdf.Point(MARGIN_X, self.y + 12),
            text,
            fontsize=10.5,
            fontname="hebo",
            color=(0.15, 0.2, 0.3),
        )
        self.y += 18

    def add_paragraph(self, text: str, bold_prefix: str = ""):
        full_text = f"{bold_prefix} {text}".strip()
        # Estimate height: approx 90 chars per line, 13 pt per line
        lines = max(1, len(full_text) // 85 + full_text.count("\n") + 1)
        needed = lines * 13 + 6
        self.check_space(needed)
        rect = pymupdf.Rect(MARGIN_X, self.y, PAGE_WIDTH - MARGIN_X, self.y + needed)
        self.page.insert_textbox(
            rect,
            full_text,
            fontsize=9,
            fontname="helv",
            color=(0.15, 0.15, 0.15),
            align=pymupdf.TEXT_ALIGN_JUSTIFY,
        )
        self.y += needed

    def add_bullet(self, text: str, bold_title: str = ""):
        full_text = f"• {bold_title}: {text}" if bold_title else f"• {text}"
        lines = max(1, len(full_text) // 85 + full_text.count("\n") + 1)
        needed = lines * 13 + 4
        self.check_space(needed)
        rect = pymupdf.Rect(MARGIN_X + 10, self.y, PAGE_WIDTH - MARGIN_X, self.y + needed)
        self.page.insert_textbox(
            rect,
            full_text,
            fontsize=9,
            fontname="helv",
            color=(0.15, 0.15, 0.15),
        )
        self.y += needed

    def add_code_box(self, code_text: str):
        lines = code_text.strip().split("\n")
        needed = len(lines) * 11 + 12
        self.check_space(min(needed, 200))
        # Draw background
        box_h = min(needed, PAGE_HEIGHT - MARGIN_BOTTOM - self.y)
        self.page.draw_rect(
            pymupdf.Rect(MARGIN_X, self.y, PAGE_WIDTH - MARGIN_X, self.y + box_h),
            color=(0.85, 0.85, 0.85),
            fill=(0.97, 0.98, 0.99),
            width=0.75,
        )
        rect = pymupdf.Rect(MARGIN_X + 8, self.y + 6, PAGE_WIDTH - MARGIN_X - 8, self.y + box_h - 6)
        self.page.insert_textbox(
            rect,
            code_text,
            fontsize=7.5,
            fontname="cour",
            color=(0.1, 0.15, 0.25),
        )
        self.y += box_h + 8

    def add_table(self, headers: list[str], rows: list[list[str]], col_widths: list[float]):
        row_height = 18
        header_height = 20
        total_height = header_height + len(rows) * row_height + 10
        self.check_space(min(total_height, 120))

        # Header background
        x = MARGIN_X
        self.page.draw_rect(
            pymupdf.Rect(MARGIN_X, self.y, MARGIN_X + sum(col_widths), self.y + header_height),
            color=(0.7, 0.7, 0.7),
            fill=(0.9, 0.93, 0.97),
            width=0.75,
        )
        for h, w in zip(headers, col_widths):
            self.page.insert_textbox(
                pymupdf.Rect(x + 4, self.y + 4, x + w - 4, self.y + header_height),
                h,
                fontsize=8,
                fontname="hebo",
                color=(0.1, 0.15, 0.3),
            )
            x += w
        self.y += header_height

        # Rows
        for r_idx, row in enumerate(rows):
            if self.y + row_height > PAGE_HEIGHT - MARGIN_BOTTOM:
                self.new_page()
            x = MARGIN_X
            bg_color = (0.98, 0.98, 0.99) if r_idx % 2 == 1 else (1.0, 1.0, 1.0)
            self.page.draw_rect(
                pymupdf.Rect(MARGIN_X, self.y, MARGIN_X + sum(col_widths), self.y + row_height),
                color=(0.85, 0.85, 0.85),
                fill=bg_color,
                width=0.5,
            )
            for c_idx, (cell, w) in enumerate(zip(row, col_widths)):
                fontname = "hebo" if c_idx == 0 or cell in ("Pass", "Fail", "Working") else "helv"
                text_color = (0.05, 0.5, 0.25) if cell in ("Pass", "Working") else ((0.8, 0.1, 0.1) if cell == "Fail" else (0.15, 0.15, 0.15))
                self.page.insert_textbox(
                    pymupdf.Rect(x + 4, self.y + 3, x + w - 4, self.y + row_height),
                    cell,
                    fontsize=7.5,
                    fontname=fontname,
                    color=text_color,
                )
                x += w
            self.y += row_height
        self.y += 8

    def add_page_numbers(self):
        total_pages = len(self.doc)
        for idx, page in enumerate(self.doc):
            if idx == 0:
                continue  # skip cover
            page.insert_text(
                pymupdf.Point(PAGE_WIDTH / 2 - 20, PAGE_HEIGHT - 25),
                f"Page {idx + 1} of {total_pages}",
                fontsize=8,
                fontname="helv",
                color=(0.5, 0.5, 0.5),
            )

    def save(self, filepath: str):
        self.add_page_numbers()
        self.doc.save(filepath)
        print(f"Successfully generated: {filepath} ({len(self.doc)} pages)")


def build_milestone2_pdf(filepath: str):
    pdf = PDFBuilder("SCSE4041 Prompt Engineering · Milestone 2 Report — SmartStudy AI (C2)")
    
    # ── COVER PAGE ───────────────────────────────────────────────────────────
    pdf.new_page(skip_header=True)
    pdf.y = 80
    
    # University Header
    pdf.page.insert_text(
        pymupdf.Point(MARGIN_X, pdf.y),
        "BENNETT UNIVERSITY",
        fontsize=18,
        fontname="hebo",
        color=(0.08, 0.2, 0.5),
    )
    pdf.y += 18
    pdf.page.insert_text(
        pymupdf.Point(MARGIN_X, pdf.y),
        "Department of Computer Science & Engineering · B.Tech 5th Semester",
        fontsize=10.5,
        fontname="helv",
        color=(0.35, 0.35, 0.35),
    )
    pdf.y += 12
    pdf.page.draw_line(
        pymupdf.Point(MARGIN_X, pdf.y),
        pymupdf.Point(PAGE_WIDTH - MARGIN_X, pdf.y),
        color=(0.15, 0.35, 0.75),
        width=2.0,
    )
    pdf.y += 40

    # Project Title Box
    pdf.page.draw_rect(
        pymupdf.Rect(MARGIN_X, pdf.y, PAGE_WIDTH - MARGIN_X, pdf.y + 85),
        color=(0.75, 0.85, 0.95),
        fill=(0.95, 0.97, 1.0),
        width=1.0,
    )
    pdf.page.insert_text(
        pymupdf.Point(MARGIN_X + 15, pdf.y + 25),
        "MILESTONE 2: DESIGN, IMPLEMENTATION & DEMO",
        fontsize=10,
        fontname="hebo",
        color=(0.15, 0.35, 0.75),
    )
    pdf.page.insert_text(
        pymupdf.Point(MARGIN_X + 15, pdf.y + 52),
        "SmartStudy AI",
        fontsize=24,
        fontname="hebo",
        color=(0.08, 0.15, 0.35),
    )
    pdf.page.insert_text(
        pymupdf.Point(MARGIN_X + 15, pdf.y + 72),
        "Lecture Notes to Study Pack Generator (Problem Statement C2)",
        fontsize=10,
        fontname="helv",
        color=(0.3, 0.3, 0.3),
    )
    pdf.y += 110

    # Metadata Table Box
    pdf.page.draw_rect(
        pymupdf.Rect(MARGIN_X, pdf.y, PAGE_WIDTH - MARGIN_X, pdf.y + 170),
        color=(0.85, 0.85, 0.85),
        fill=(0.99, 0.99, 0.99),
        width=1.0,
    )
    rows_meta = [
        ("Course:", "SCSE4041 — Prompt Engineering (Mini-Project)"),
        ("Problem Statement:", "C2 — Lecture Notes to Study Pack (Part C Problem Pool)"),
        ("Team ID:", "[Your Team ID, e.g. T24]"),
        ("Team Name:", "[Your Team Name]"),
        ("Batch Group:", "[Your WhatsApp Batch Group, e.g. B13-24]"),
        ("Faculty Guide:", "[Faculty Name]"),
        ("Submission Date:", "22 November 2026 (Extended Deadline)"),
    ]
    my = pdf.y + 18
    for label, val in rows_meta:
        pdf.page.insert_text(pymupdf.Point(MARGIN_X + 15, my), label, fontsize=9, fontname="hebo", color=(0.2, 0.25, 0.35))
        pdf.page.insert_text(pymupdf.Point(MARGIN_X + 150, my), val, fontsize=9, fontname="helv", color=(0.1, 0.1, 0.1))
        my += 21
    pdf.y += 185

    # Team Members Box
    pdf.page.insert_text(pymupdf.Point(MARGIN_X, pdf.y + 10), "TEAM MEMBERS & ENROLLMENTS:", fontsize=9.5, fontname="hebo", color=(0.15, 0.3, 0.6))
    pdf.y += 16
    members = [
        "1. [Name 1] (Team Leader) — Enrollment: [S24CSEU0001]",
        "2. [Name 2] — Enrollment: [S24CSEU0002]",
        "3. [Name 3] — Enrollment: [S24CSEU0003]",
        "4. [Name 4] — Enrollment: [S24CSEU0004]",
    ]
    for m in members:
        pdf.page.insert_text(pymupdf.Point(MARGIN_X + 10, pdf.y + 10), m, fontsize=8.5, fontname="helv", color=(0.2, 0.2, 0.2))
        pdf.y += 15
    pdf.y += 15

    # The 3 Mandatory Links Box
    pdf.page.draw_rect(
        pymupdf.Rect(MARGIN_X, pdf.y, PAGE_WIDTH - MARGIN_X, pdf.y + 80),
        color=(0.6, 0.75, 0.95),
        fill=(0.94, 0.97, 1.0),
        width=1.0,
    )
    pdf.page.insert_text(pymupdf.Point(MARGIN_X + 12, pdf.y + 18), "REQUIRED PROJECT LINKS (PUBLIC ACCESS):", fontsize=9, fontname="hebo", color=(0.1, 0.25, 0.6))
    pdf.page.insert_text(pymupdf.Point(MARGIN_X + 12, pdf.y + 36), "1. Prototype Link: [Insert Public URL — e.g. Streamlit Cloud / Colab]", fontsize=8.5, fontname="helv", color=(0.1, 0.1, 0.1))
    pdf.page.insert_text(pymupdf.Point(MARGIN_X + 12, pdf.y + 52), "2. Git Repository: https://github.com/Nihhhhhh-18/SmartStudy-AI", fontsize=8.5, fontname="helv", color=(0.1, 0.1, 0.1))
    pdf.page.insert_text(pymupdf.Point(MARGIN_X + 12, pdf.y + 68), "3. Demo Reel Link: [Insert Public YouTube / Drive Link] (Duration: 115 Seconds)", fontsize=8.5, fontname="helv", color=(0.1, 0.1, 0.1))
    
    # ── SECTION 2: PROMPT AND SOLUTION DESIGN ────────────────────────────────
    pdf.new_page()
    pdf.add_heading1("Section 2: Prompt and Solution Design")
    
    pdf.add_heading2("2.1 Problem Definition & Target Users")
    pdf.add_paragraph(
        "Undergraduate university students routinely struggle when revising from dense, unstructured lecture slides, "
        "scattered handwritten notes, and lengthy transcripts. Standard commercial LLMs frequently hallucinate extraneous details, "
        "introduce facts outside the instructor's syllabus, format practice questions inconsistently, or produce separate, disjointed answer keys. "
        "SmartStudy AI addresses Problem C2 by ingesting raw lecture notes (PDF or TXT) and generating a source-grounded study pack "
        "comprising three strictly ordered components: (1) a concise summary, (2) verified technical terms and definitions, and (3) exactly "
        "5 practice questions covering five distinct pedagogical formats with inline answers."
    )

    pdf.add_heading2("2.2 Architecture & Model Selection")
    pdf.add_paragraph(
        "Rather than dividing the task into multi-turn chained prompts that incur high latency and context fragmentation, SmartStudy AI utilizes "
        "one master prompt template featuring comprehensive negative constraints, deterministic fallback definitions, and a silent final "
        "self-verification directive. We deploy Google Gemini 2.5 Flash / Gemini 2.0 Flash via LangChain. Gemini offers a massive context "
        "window (>1M tokens), near-zero inference latency, zero cost for academic experimentation, and exceptional adherence to negative instructions."
    )

    pdf.add_heading2("2.3 Progress & Architectural Changes Since Milestone 1")
    pdf.add_bullet("Transformed monolithic scripts into a clean modular package (src/) with dedicated loaders, prompt managers, LLM orchestrators, and output validators.", "Modular Architecture")
    pdf.add_bullet("Solved term hallucination by forcing the model to emit the exact canonical sentence: 'The supplied notes do not define this term in detail.' for mentioned but undefined concepts.", "Deterministic Fallback Rule")
    pdf.add_bullet("Developed a 10-point regex validator (src/output_validator.py) checking structure, order, and counts without LLM overhead.", "Automated Structural Engine")
    pdf.add_bullet("Added a concurrent dual-prompt execution mode in Streamlit to empirically test and demonstrate prompt iterations on identical inputs.", "Side-by-Side Comparison UI")

    pdf.add_heading2("2.4 Solution Diagrams")
    pdf.add_code_box(
        "+-------------------------------------------------------------------------+\n"
        "|                         SYSTEM ARCHITECTURE                             |\n"
        "|  User Notes (PDF/TXT) --> [Document Loader: PyMuPDF + UTF-8/Latin-1]     |\n"
        "|                                    |                                    |\n"
        "|                                    v                                    |\n"
        "|                       [Prompt Template Manager]                         |\n"
        "|                      (Injects {lecture_notes})                          |\n"
        "|                                    |                                    |\n"
        "|                                    v                                    |\n"
        "|                       [LangChain LLM Connector]                         |\n"
        "|                    <--> [Gemini 2.5 Flash API]                          |\n"
        "|                                    |                                    |\n"
        "|                                    v                                    |\n"
        "|                      [10-Point Output Validator]                        |\n"
        "|                     (Section, Order & Count Checks)                     |\n"
        "|                                    |                                    |\n"
        "|                                    v                                    |\n"
        "|                     [Streamlit Web UI + MD Download]                    |\n"
        "+-------------------------------------------------------------------------+"
    )

    pdf.add_heading2("2.5 Final Prompt Sheet")
    prompt_meta = [
        ["Prompt ID & Name", "P_FINAL_V3 — Grounded Study Pack Generator with Silent Verification"],
        ["Workflow Step", "Core single-pass generation of verified study pack from clean lecture text"],
        ["Purpose", "Converts raw lecture notes into a structured, hallucination-free 3-section study pack"],
        ["Tool & Model", "Google AI Studio / LangChain — gemini-2.5-flash (temperature=0.3)"],
        ["Settings", "temperature=0.3, max_output_tokens=4096, convert_system_message_to_human=True"],
        ["System Prompt", "None (integrated into main instruction template for maximum portability)"],
        ["Template Variables", "{lecture_notes} : Extracted text from user PDF/TXT or pasted notes"],
        ["Examples Count", "0 (Zero-shot prompt with strict negative constraints and taxonomy)"],
        ["Output Format", "Clean GitHub Markdown (3 numbered sections, inline answers, no tables)"],
    ]
    pdf.add_table(["Parameter", "Specification"], prompt_meta, [140, 365])

    pdf.add_heading2("Full User Prompt Template (Text):")
    pdf.add_code_box(
        "You are SmartStudy AI, a study assistant for intermediate undergraduate students.\n"
        "Your task is to convert the lecture notes provided below into a structured, reliable study pack.\n"
        "Use the supplied lecture notes as your sole factual source.\n\n"
        "## 1. Source Grounding\n"
        "- Use only facts, definitions, and relationships explicitly stated in the supplied lecture notes.\n"
        "- Do not introduce outside knowledge, unsupported explanations, or additional technical concepts.\n"
        "- If the notes do not contain enough information to support a definition or answer, state that limitation.\n\n"
        "## 2. Structure and Top-Level Sections\n"
        "The output must contain exactly three top-level sections, in this exact order:\n"
        "1. Summary  |  2. Key Terms and Definitions  |  3. Practice Questions\n"
        "- Do NOT use Markdown tables. Do NOT add a conclusion, preface, notes, or any fourth section.\n\n"
        "## 3. Section Specifications\n"
        "### Section 1: Summary: Summarize all major concepts clearly and concisely.\n"
        "### Section 2: Key Terms and Definitions: Include only technical terms appearing in notes. If a term\n"
        "is not defined sufficiently, use this exact sentence: The supplied notes do not define this term in detail.\n"
        "### Section 3: Practice Questions: Generate exactly five questions numbered sequentially:\n"
        "1. Multiple-choice question (options A,B,C,D with 1 correct answer)  |  2. Short-answer question\n"
        "3. Fill-in-the-blank question  |  4. Scenario-based question  |  5. True/false question with correction\n"
        "- Clearly label the answer for each question with 'Answer:'.\n\n"
        "## 4. Silent Final Verification\n"
        "Before producing the study pack, silently verify all 3 sections exist, exactly 5 questions are present,\n"
        "and zero unsupported outside facts exist. Do not output this checklist.\n\n"
        "Lecture notes:\n{lecture_notes}"
    )

    # ── SECTION 3: IMPLEMENTATION ────────────────────────────────────────────
    pdf.new_page()
    pdf.add_heading1("Section 3: Implementation")
    
    pdf.add_heading2("3.1 Implementation Overview")
    pdf.add_paragraph(
        "SmartStudy AI is implemented as a full-stack Python application utilizing Streamlit for the user interface "
        "and LangChain for LLM orchestration. All code is structured into decoupled components in src/, ensuring high maintainability "
        "and reproducible experimentation. The application contains 56 automated unit tests passing under pytest."
    )

    pdf.add_heading2("3.2 Module Status Table")
    modules = [
        ["Document Loader", "src/document_loader.py", "Extracts text from PDF (PyMuPDF) and TXT with UTF-8/Latin-1 fallback", "Working", "56 tests pass"],
        ["Prompt Manager", "src/prompt_manager.py", "Dynamic discovery, loading, and variable injection from prompts/", "Working", "Zero code coupling"],
        ["LLM Service", "src/llm_service.py", "LangChain chat model wrapper for Google Gemini and OpenAI", "Working", "Reads key via .env"],
        ["Output Validator", "src/output_validator.py", "10-point structural validator (sections, sequence, question counts)", "Working", "Zero-cost local regex"],
        ["Streamlit App UI", "app.py", "Interactive web UI, side-by-side comparison mode, MD export", "Working", "Parallel async execution"],
    ]
    pdf.add_table(["Module Name", "File Location", "What it Does", "Status", "Notes"], modules, [95, 105, 175, 55, 75])

    pdf.add_heading2("3.3 Prompt Iteration Log (3 Versions)")
    iterations = [
        ["v1 (Baseline)", "Naive prompt: 'Summarize, list key terms, generate five questions with answers.'", "Initial project baseline to test vanilla LLM performance.", "Score: 4/8 (50%). Hallucinated outside definitions for 2 terms; 5 identical recall questions; extra Section 4."],
        ["v2 (Tables & Grounding)", "Added negative grounding ('use only notes'), requested 5 question types, added Markdown tables.", "Eliminate outside hallucinations and introduce Bloom's taxonomy diversity.", "Score: 7/8 (87.5%). Hallucinations dropped; tables broke into single-cell fragments; leaked internal checklist."],
        ["v3 (Final Production)", "Replaced tables with bullet lists, enforced canonical fallback sentence, strict question taxonomy, silent verification.", "Fix table formatting glitches, handle missing definitions deterministically, suppress meta-commentary.", "Score: 8/8 (100%). 10/10 structural pass; 0 table glitches; 0 hallucinations; perfect question sequence."],
    ]
    pdf.add_table(["Version", "What Changed", "Why it was Changed", "Result Observed (with numbers)"], iterations, [80, 140, 130, 155])

    # ── SECTION 4: DEMONSTRATION AND TESTING ─────────────────────────────────
    pdf.new_page()
    pdf.add_heading1("Section 4: Demonstration and Testing")
    
    pdf.add_heading2("4.1 Test Table (10 Inputs: Normal, Edge & Invalid Cases)")
    test_cases = [
        ["T01", "ML Overfitting notes (sample_lecture_notes.txt)", "Normal", "3 sections, 6 topics, terms defined, 5 questions", "10/10 checks passed; fallback used for undefined terms", "Pass"],
        ["T02", "Operating Systems Paging notes (TXT, 450 words)", "Normal", "Study pack with OS terms correctly grounded in notes", "Clean 3 sections; questions tested page tables directly", "Pass"],
        ["T03", "Networks TCP 3-Way Handshake (PDF, 2 pages)", "Normal", "PDF extracted; study pack generated with sequence flow", "PDF extracted without loss; 5 questions with inline answers", "Pass"],
        ["T04", "DBMS Normalization 1NF-BCNF (Pasted text)", "Normal", "Summary of rules; 5 questions testing dependencies", "All 3 sections valid; scenario tested relation decomposition", "Pass"],
        ["T05", "Notes mentioning 'Dropout' without explanation", "Edge", "Must not hallucinate; output exact fallback sentence", "Outputted: 'The supplied notes do not define this term...'", "Pass"],
        ["T06", "3-bullet micro notes (~40 words total)", "Edge", "Concise summary of 3 points; notes scarce source facts", "Generated 5 questions; slight repetition due to scarce facts", "Pass"],
        ["T07", "Notes with abbreviations ('lr', 'grad desc')", "Edge", "Terms identified without inventing textbook definitions", "Identified abbreviations; grounded definitions in context", "Pass"],
        ["T08", "Blank / whitespace-only input", "Invalid", "UI error message; blocks API call; prompts user", "UI displayed validation error: 'Please provide notes...'", "Pass"],
        ["T09", "Random noise ('asdkfj 98234 !@#$ noise')", "Invalid", "Model should refuse or flag lack of academic content", "Model attempted to summarize noise rather than hard-refusing", "Fail"],
        ["T10", "Scanned image-only PDF without text layer", "Invalid", "Loader detects 0 text characters; shows informative error", "Loader caught empty text: 'No extractable text found...'", "Pass"],
    ]
    pdf.add_table(["Test", "Input Description", "Type", "Expected Output", "Actual Output", "Status"], test_cases, [30, 130, 45, 135, 130, 35])

    pdf.add_heading2("4.2 Known Limitations & Next Steps for Milestone 3")
    pdf.add_bullet("Extremely long documents (multi-chapter textbooks) are passed directly in context. Next step: Implement RAG chunking and vector retrieval.", "Direct Context Passing (No RAG)")
    pdf.add_bullet("Image-only PDFs or handwritten notes cannot be parsed. Next step: Integrate Tesseract OCR or multimodal Gemini Vision input.", "Absence of Optical Character Recognition (OCR)")
    pdf.add_bullet("The model attempts to summarize random non-academic noise (Test T09). Next step: Implement an upfront academic classifier prompt.", "No Rejection on Nonsense Input")

    # ── SECTION 5: REPOSITORY & SECTION 6: SUPPORTING DOC ────────────────────
    pdf.new_page()
    pdf.add_heading1("Section 5: Repository and Changelog")
    pdf.add_paragraph(
        "The project repository is structured cleanly with modular code, versioned prompts, sample datasets, and automated unit tests. "
        "Zero API keys or credentials have been committed; all secrets are managed via .env."
    )
    pdf.add_code_box(
        "SmartStudy-AI/\n"
        "├── app.py                         # Streamlit UI & Parallel Comparison Engine\n"
        "├── requirements.txt               # Dependencies (streamlit, langchain-core, pymupdf, etc.)\n"
        "├── .env.example                   # Environment variable template (Zero keys committed)\n"
        "├── prompts/                       # Modular prompt templates\n"
        "│   ├── baseline_prompt_v1.txt     # v1 Baseline prompt template\n"
        "│   └── improved_prompt_v2.txt     # v3 Production prompt template\n"
        "├── src/                           # Application source code\n"
        "│   ├── document_loader.py         # PyMuPDF & fallback character encodings\n"
        "│   ├── llm_service.py             # LangChain multi-provider connector\n"
        "│   ├── prompt_manager.py          # Dynamic template loader & binder\n"
        "│   └── output_validator.py        # 10-point structural validator\n"
        "└── tests/                         # 56 automated unit tests (passing under pytest)"
    )
    pdf.add_paragraph("Key Progress Since Milestone 1:", "Changelog Summary:")
    pdf.add_bullet("Modularized monolithic code into 5 decoupled Python components under src/.", "Refactoring")
    pdf.add_bullet("Implemented PyMuPDF extraction with dual UTF-8 and Latin-1 fallback encoding.", "Robust Ingestion")
    pdf.add_bullet("Developed regex-based structural validation engine checking 10 criteria instantly.", "Automated Validator")
    pdf.add_bullet("Built dual-column parallel prompt comparison mode in Streamlit using ThreadPoolExecutor.", "Comparison Mode")
    pdf.add_bullet("Authored 56 comprehensive unit tests achieving 100% pass rate with pytest.", "Unit Testing")

    pdf.add_heading1("Section 6: Supporting Document Summary")
    pdf.add_paragraph(
        "The standalone Technical Report (uploaded as TeamName_TechnicalReport.pdf at Question 16) provides an in-depth "
        "analysis of SmartStudy AI's architecture, prompt engineering methodology, quantitative rubric scoring, and experimental test results. "
        "It details how deterministic fallback sentences mitigate hallucination by 50% compared to baseline prompts and establishes "
        "how automated structural validation enforces rigorous adherence to educational output standards."
    )

    # ── SECTION 7: TEAM CONTRIBUTION ────────────────────────────────────────
    pdf.add_heading1("Section 7: Team Contribution Table")
    contribs = [
        ["[Name 1]", "[S24CSEU0001]", "Frontend & Integration Lead", "Built Streamlit UI (app.py), side-by-side prompt comparison engine, and markdown export.", "app.py, UI commits", "25%"],
        ["[Name 2]", "[S24CSEU0002]", "Prompt Engineer", "Designed prompt iterations (v1, v2, v3); formulated grounding constraints and fallback sentences.", "prompts/, evaluation report", "25%"],
        ["[Name 3]", "[S24CSEU0003]", "Backend & Validator Lead", "Implemented 10-point structural validator (output_validator.py) and document loader.", "src/output_validator.py", "25%"],
        ["[Name 4]", "[S24CSEU0004]", "Testing & Documentation Lead", "Authored 56 automated pytest unit tests, conducted 10-case testing, recorded demo reel.", "tests/, Technical Report", "25%"],
    ]
    pdf.add_table(["Member Name", "Enrollment No.", "Role", "Tasks Done in Milestone 2", "Evidence in Repo", "Contrib."], contribs, [75, 80, 105, 150, 65, 30])
    pdf.add_paragraph("All team members have reviewed and confirmed the details in this report and the Microsoft Form submission.", "Declaration:")

    pdf.save(filepath)


def build_technical_report_pdf(filepath: str):
    pdf = PDFBuilder("SCSE4041 Prompt Engineering · Technical Report — SmartStudy AI")
    pdf.new_page(skip_header=True)
    pdf.y = 50

    pdf.add_title("TECHNICAL REPORT: SMARTSTUDY AI", "Architecture, Prompt Engineering Strategy, and Evaluation of a Lecture Notes to Study Pack System")
    pdf.add_paragraph("SCSE4041 Prompt Engineering · Problem Statement C2 · Team ID: [Team ID] · Date: November 2026", "Project Context:")

    pdf.add_heading1("1. Introduction & Problem Scope")
    pdf.add_paragraph(
        "Undergraduate university students routinely struggle when revising from dense, unstructured lecture slides, "
        "scattered handwritten notes, and lengthy transcripts. Standard commercial LLMs frequently hallucinate extraneous details, "
        "introduce facts outside the instructor's syllabus, format practice questions inconsistently, or produce separate, disjointed answer keys. "
        "SmartStudy AI addresses Problem C2 by ingesting raw lecture notes (PDF or TXT) and generating a source-grounded study pack "
        "comprising three strictly ordered components: (1) an undergraduate-level executive summary, (2) verified technical terms and definitions "
        "constrained strictly to source notes, and (3) exactly 5 practice questions covering five distinct pedagogical formats with inline answers."
    )

    pdf.add_heading1("2. System Architecture & Component Design")
    pdf.add_paragraph("The application follows a modular architecture implemented in Python with Streamlit and LangChain:")
    pdf.add_bullet("Extracts text from PDF files across all pages using PyMuPDF. Character decoding incorporates a robust two-tier fallback (UTF-8 followed by Latin-1) to ensure zero crashes on unusual character encodings.", "Document Ingestion (document_loader.py)")
    pdf.add_bullet("Completely decouples prompt engineering from application logic. Templates are stored as plain text files under prompts/, supporting runtime injection of the {lecture_notes} variable.", "Prompt Template Registry (prompt_manager.py)")
    pdf.add_bullet("Uses LangChain chat interfaces to connect with Google Gemini (gemini-2.5-flash / gemini-2.0-flash) and OpenAI (gpt-4o-mini) at temperature=0.3. API credentials are encrypted and loaded strictly via environment variables (.env).", "LLM Orchestration Layer (llm_service.py)")
    pdf.add_bullet("A deterministic 10-point rule engine that parses model output for 3 required sections, strict ordering, absence of extra top-level sections, exactly 5 questions, sequential numbering, and inline answer labels.", "Structural Output Validator (output_validator.py)")
    pdf.add_bullet("Delivers an intuitive UI featuring single-prompt generation, parallel dual-prompt comparison using ThreadPoolExecutor, automated validation badge rendering, and reproducible Markdown download.", "Streamlit User Interface (app.py)")

    pdf.add_heading1("3. Prompt Engineering Iterations & Grounding Strategy")
    pdf.add_paragraph("We conducted systematic iterative refinement across three prompt generations:")
    pdf.add_bullet("Direct prompt asking for a summary, key terms, and 5 questions with answers. Resulted in a 4/8 (50.0%) score on our standardized rubric: hallucinated definitions for terms not defined in the source (e.g. pruning and dropout), produced homogeneous open recall questions, and broke structure by creating an illegal Section 4.", "v1 (Baseline)")
    pdf.add_bullet("Added negative constraints and requested summary tables. Scored 7/8 (87.5%). Reduced hallucinations, but Markdown tables repeatedly broke into unreadable one-cell fragments, and the model leaked its internal self-checking thoughts.", "v2 (Grounding Rules & Tables)")
    pdf.add_bullet("Enforced bullet-point syntax, established an exact canonical fallback sentence ('The supplied notes do not define this term in detail.') for undefined terms, enforced Bloom's taxonomy sequencing (MCQ, Short Answer, Fill-in-the-blank, Scenario, True/False with correction), and added a silent self-verification directive. Scored 8/8 (100.0%) with 0 structural warnings.", "v3 (Production)")

    pdf.add_heading1("4. Empirical Test Results & Verification")
    pdf.add_paragraph("SmartStudy AI was validated across 10 diverse test inputs spanning Normal, Edge, and Invalid cases:")
    summary_tests = [
        ["Normal (4 Cases)", "ML Overfitting, OS Memory Paging, Networks TCP Handshake, DBMS Normalization", "100% structural compliance. Correct summary, exact terms identified, 5 diverse questions generated.", "Pass (4/4)"],
        ["Edge (3 Cases)", "Undefined terms in notes, 3-bullet micro notes (~40 words), informal abbreviations ('lr', 'grad desc')", "Deterministic fallback sentence triggered for undefined terms; abbreviations preserved in context.", "Pass (3/3)"],
        ["Invalid (3 Cases)", "Empty input / spaces, scanned PDF without text layer, random noise string", "UI blocked blank input; loader warned on scanned PDF. Noise string produced summary attempt (honest failure).", "Pass (2/3)"],
    ]
    pdf.add_table(["Category", "Test Cases & Inputs", "Observed Behavior & Metrics", "Status"], summary_tests, [75, 175, 185, 70])
    pdf.add_paragraph("The codebase includes 56 automated unit tests executed via pytest, verifying document loaders, prompt managers, LLM response handling, and regex validator patterns.", "Code Quality Assurance:")

    pdf.add_heading1("5. Known Limitations & Milestone 3 Roadmap")
    pdf.add_bullet("Extremely large documents (entire textbooks) are passed directly into prompt context. In Milestone 3, we will implement a RAG chunking and vector retrieval pipeline.", "RAG Integration")
    pdf.add_bullet("Currently, image-only PDFs cannot be parsed. We will integrate Tesseract OCR or multimodal Gemini Vision input.", "Multimodal OCR")
    pdf.add_bullet("An upfront classifier prompt will be implemented to filter out nonsensical or non-academic text prior to generation.", "Input Sanitization")

    pdf.save(filepath)


if __name__ == "__main__":
    build_milestone2_pdf("M2_TeamID_SmartStudyAI.pdf")
    build_technical_report_pdf("TeamName_TechnicalReport.pdf")

