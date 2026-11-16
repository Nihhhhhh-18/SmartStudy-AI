# 📚 SmartStudy AI

**Lecture Notes → Study Pack Generator**

SmartStudy AI converts your lecture notes into a structured study pack containing:

1. **Summary** — A concise overview of the main concepts.
2. **Key Terms & Definitions** — Technical terms grounded in the supplied notes.
3. **Practice Questions** — Exactly 5 questions with answers (mixed question types).

Built for a **Prompt Engineering** academic project, the app keeps prompt templates separate from application logic so different prompt versions can be tested and compared.

---

## ✨ Features

- Upload **PDF** or **TXT** lecture notes, or **paste text** directly.
- Choose between **Baseline (V1)** and **Improved (V2)** prompt templates.
- **Comparison mode** — run both prompts side-by-side on the same notes.
- **Structural validation** — checks for the 3 required sections and exactly 5 questions.
- **Download** the generated study pack as a Markdown file.
- Configurable LLM provider (**Google Gemini** or **OpenAI**) via environment variables.
- No API keys hardcoded or displayed — everything loads from `.env`.

---

## 📁 Project Structure

```
SmartStudy-AI/
├── app.py                         # Streamlit UI (entry point)
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variable template
├── .gitignore                     # Files excluded from Git
├── README.md                      # This file
│
├── prompts/                       # Prompt templates (LangChain-ready)
│   ├── baseline_prompt_v1.txt     # V1 — baseline prompt
│   └── improved_prompt_v2.txt     # V2 — improved grounding & formatting
│
├── src/                           # Application source code
│   ├── __init__.py
│   ├── document_loader.py         # TXT & PDF text extraction
│   ├── llm_service.py             # LangChain LLM configuration & invocation
│   ├── prompt_manager.py          # Load & manage prompt templates
│   └── output_validator.py        # Structural validation of LLM output
│
├── tests/                         # Unit tests (no API key required)
│   ├── test_document_loader.py    # Document loading & extraction tests
│   ├── test_prompt_manager.py     # Prompt template loading & distinctness tests
│   ├── test_output_validator.py   # Comprehensive 10-point structural validator tests
│   ├── test_llm_service.py        # LLM response content extraction tests
│   └── test_app_comparison.py     # Streamlit comparison & selection logic tests
│
├── sample_data/                   # Example inputs
│   └── sample_lecture_notes.txt
│
├── evaluation_report_v1_vs_v2.md  # Head-to-head empirical evaluation report
│
│  ── Original experiment artifacts (preserved) ──
├── baseline_prompt_v1.txt         # Original V1 prompt (with embedded notes)
├── improved_prompt_v2.txt         # Original V2 prompt (with embedded notes)
├── baseline_output_v1.txt         # Historical V1 model output
├── improved_output_v2.txt         # Historical V2 model output
├── evaluation_v1.txt              # Historical V1 rubric evaluation (75%)
├── evaluation_v2.txt              # Historical V2 rubric evaluation (87.5%)
└── sample_lecture_notes.txt       # Original sample notes
```

---

## 🚀 Quick Start

### 1. Prerequisites

- **Python 3.11+** (tested with 3.14)
- **pip** (comes with Python)
- A terminal (Terminal.app on Mac)

### 2. Create a virtual environment

```bash
cd path/to/SmartStudy-AI

python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your API key

```bash
cp .env.example .env
```

Then open `.env` in any text editor and replace the placeholder:

```dotenv
LLM_PROVIDER=google
LLM_MODEL=gemini-3.5-flash
LLM_API_KEY=your-actual-api-key
```

| Provider | Recommended Model | Get your key from |
|----------|-------------------|-------------------|
| Google (Gemini) | `gemini-3.5-flash` | https://aistudio.google.com/apikey |
| OpenAI | `gpt-4o-mini` | https://platform.openai.com/api-keys |

> ⚠️ **Never commit `.env` to Git.** It is already in `.gitignore`.

### 5. Run the app

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

---

## 🧪 Prompt Experimentation

### Selecting a prompt version

In the **sidebar**, use the **Prompt version** dropdown to choose:

- **V1 — Baseline**: A straightforward prompt asking for a summary, key terms, and 5 questions.
- **V2 — Improved (recommended)**: Adds grounding constraints, explicit instructions to only use terms from the notes, and a final self-check.

### Comparison mode

Toggle **🔬 Comparison mode** in the sidebar. Both V1 and V2 will run on the same notes and results appear side by side.

### Downloaded files

Each downloaded `.md` file includes metadata comments recording:
- Which prompt version was used
- Which model was used
- The timestamp

This makes experiment results reproducible.

---

## 🧪 Running Tests

All tests run **without an API key** — they test text extraction, prompt loading, and output validation only.

```bash
# Make sure you're in the venv
source venv/bin/activate

# Run all tests
pytest tests/ -v
```

---

## ⚠️ Current Limitations

1. **No OCR** — Image-only or scanned PDFs cannot be processed. The app will explain this and ask you to provide a text-based PDF or paste the notes.
2. **Structural validation only** — The app checks that the output has 3 sections and 5 questions. It does **not** verify factual correctness.
3. **API key required** — An LLM API key is needed for study pack generation. Text extraction and the UI can be tested without one.
4. **No vector database / RAG** — Notes are passed directly in the prompt. Very long documents may exceed the model's context window.

---

## 📖 How It Works (Architecture)

```
User uploads notes
       │
       ▼
 document_loader.py   ← Extract text (PDF/TXT)
       │
       ▼
 prompt_manager.py    ← Load selected prompt template
       │
       ▼
  llm_service.py      ← Send prompt + notes to LLM via LangChain
       │
       ▼
output_validator.py   ← Check structure (sections, question count)
       │
       ▼
    app.py            ← Display results + download option
```

---

## 🤝 Contributing

This is an academic project. If you'd like to add a new prompt version:

1. Create `prompts/your_prompt_v3.txt` with a `{lecture_notes}` placeholder.
2. Register it in `src/prompt_manager.py` → `PROMPT_VERSIONS` dict.
3. Run the app, test with sample notes, and document your evaluation.

---

## 📄 License

Academic project — for educational use.
