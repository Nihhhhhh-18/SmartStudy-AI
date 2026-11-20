"""
app.py — SmartStudy AI  ·  Lecture Notes → Study Pack Generator

Run with:
    streamlit run app.py
"""

import datetime
import os
import streamlit as st

from src.document_loader import load_document, validate_text
from src.prompt_manager import (
    list_prompt_versions,
    load_prompt_template,
    get_prompt_filename,
    DEFAULT_VERSION,
)
from src.llm_service import (
    generate_study_pack,
    get_llm_info,
    is_api_key_configured,
    LLMConfigError,
)
from src.output_validator import validate_output, analyze_output, MANUAL_GROUNDING_CHECKLIST

# ═══════════════════════════════════════════════════════════════════════════
# Page configuration
# ═══════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="SmartStudy AI",
    page_icon="📚",
    layout="wide",
)

# ═══════════════════════════════════════════════════════════════════════════
# Custom CSS for a clean, professional look
# ═══════════════════════════════════════════════════════════════════════════
st.markdown(
    """
    <style>
    /* ── Global ──────────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* ── Header gradient ─────────────────────────────────────── */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    .main-header h1 { margin: 0; font-size: 2.4rem; font-weight: 700; }
    .main-header p  { margin: 0.5rem 0 0; opacity: 0.92; font-size: 1.1rem; }

    /* ── Cards ────────────────────────────────────────────────── */
    .card {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        backdrop-filter: blur(6px);
    }

    /* ── Validation badges ───────────────────────────────────── */
    .validation-pass {
        background: #064e3b; color: #6ee7b7;
        padding: 0.6rem 1rem; border-radius: 8px;
        font-size: 0.95rem; margin-bottom: 0.5rem;
    }
    .validation-warn {
        background: #78350f; color: #fcd34d;
        padding: 0.6rem 1rem; border-radius: 8px;
        font-size: 0.95rem; margin-bottom: 0.5rem;
    }

    /* ── Divider ──────────────────────────────────────────────── */
    .section-divider {
        height: 2px;
        background: linear-gradient(90deg, #667eea, #764ba2, #667eea);
        border: none; margin: 1.5rem 0;
        border-radius: 1px;
    }

    /* ── Streamlit overrides ─────────────────────────────────── */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; border: none; border-radius: 8px;
        padding: 0.5rem 1.6rem; font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ═══════════════════════════════════════════════════════════════════════════
# Header
# ═══════════════════════════════════════════════════════════════════════════
st.markdown(
    """
    <div class="main-header">
        <h1>📚 SmartStudy AI</h1>
        <p>Transform your lecture notes into a structured study pack — summary, key terms, and practice questions.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ═══════════════════════════════════════════════════════════════════════════
# Sidebar — settings & information
# ═══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.header("⚙️ Settings")

    # Prompt version selector
    versions = list_prompt_versions()
    default_idx = versions.index(DEFAULT_VERSION) if DEFAULT_VERSION in versions else 0
    selected_version = st.selectbox(
        "Prompt version",
        versions,
        index=default_idx,
        help="Choose the prompt template used to generate the study pack.",
    )

    # Comparison mode toggle
    comparison_mode = st.checkbox(
        "🔬 Comparison mode",
        value=False,
        help="Run both V1 and V2 prompts on the same notes and display results side by side.",
    )

    st.markdown("---")

    # LLM info (no secrets)
    st.subheader("🤖 Model Info")
    try:
        info = get_llm_info()
        st.markdown(f"**Provider:** `{info['provider']}`")
        st.markdown(f"**Model:** `{info['model']}`")
    except Exception:
        st.warning("LLM not configured yet — see .env.example")

    # API key status and session override
    key_configured = is_api_key_configured()
    if key_configured:
        st.success("🔑 API Key active")
    else:
        st.warning("⚠️ No API Key in Secrets or .env")

    manual_key = st.text_input(
        "🔑 API Key (Session Override)",
        type="password",
        placeholder="Paste Google or OpenAI API key…",
        help="Paste your API key here if not configured in Streamlit Secrets. Stays strictly in memory for this session.",
    )
    if manual_key.strip():
        os.environ["LLM_API_KEY"] = manual_key.strip()
        os.environ["GOOGLE_API_KEY"] = manual_key.strip()
        st.info("Using session API key override.")

    st.markdown("---")
    st.caption(
        "SmartStudy AI checks the **structure** of the generated study pack "
        "(sections present, question count). It does **not** guarantee factual "
        "correctness. Always review the output against your original notes."
    )

# ═══════════════════════════════════════════════════════════════════════════
# Input area
# ═══════════════════════════════════════════════════════════════════════════
st.subheader("📝 Provide Your Lecture Notes")

input_method = st.radio(
    "Choose input method:",
    ["Upload a file (PDF or TXT)", "Paste text directly"],
    horizontal=True,
)

lecture_text: str = ""
input_error: str | None = None

if input_method == "Upload a file (PDF or TXT)":
    uploaded_file = st.file_uploader(
        "Upload your lecture notes",
        type=["pdf", "txt"],
        help="Supported formats: PDF (text-based) and TXT.",
    )
    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        lecture_text, input_error = load_document(uploaded_file.name, file_bytes)
else:
    pasted = st.text_area(
        "Paste your lecture notes here",
        height=250,
        placeholder="Paste lecture notes or slide content…",
    )
    if pasted:
        lecture_text = pasted

# ═══════════════════════════════════════════════════════════════════════════
# Generate button
# ═══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

generate_clicked = st.button(
    "🚀 Generate Study Pack",
    type="primary",
    use_container_width=True,
)


def _run_generation(notes: str, version_name: str) -> tuple[str, list[str], str, dict]:
    """Run a single generation and return (output, warnings, prompt_file, analysis)."""
    prompt_tpl = load_prompt_template(version_name)
    result = generate_study_pack(notes, prompt_tpl)
    analysis = analyze_output(result)
    warnings = analysis["warnings"]
    prompt_file = get_prompt_filename(version_name)
    return result, warnings, prompt_file, analysis


def _display_result(
    output: str,
    warnings: list[str],
    version_name: str,
    prompt_file: str,
    model_info: dict[str, str],
    analysis: dict | None = None,
) -> None:
    """Render one study-pack result in the Streamlit UI."""
    # Metadata
    st.caption(
        f"Prompt: **{version_name}** (`{prompt_file}`) · "
        f"Model: `{model_info['provider']}/{model_info['model']}`"
    )

    # Validation results
    if warnings:
        for w in warnings:
            st.markdown(f'<div class="validation-warn">⚠️ {w}</div>', unsafe_allow_html=True)
        st.info(
            "ℹ️ These warnings check **structure only** (sections, ordering, question count, and answer labels). "
            "They do not verify factual correctness. The original response is shown below."
        )
    else:
        st.markdown(
            '<div class="validation-pass">✅ All structural checks passed '
            '(3 sections in order, 5 questions detected with answers).</div>',
            unsafe_allow_html=True,
        )
        st.info(
            "ℹ️ Structural checks passed. This does **not** guarantee factual correctness — "
            "please review the output against your original notes."
        )

    # The actual study pack
    st.markdown(output)

    # Download button
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    download_name = f"study_pack_{version_name.split()[0].lower()}_{timestamp}.md"
    download_content = (
        f"<!-- SmartStudy AI Study Pack -->\n"
        f"<!-- Prompt: {version_name} ({prompt_file}) -->\n"
        f"<!-- Model: {model_info['provider']}/{model_info['model']} -->\n"
        f"<!-- Generated: {timestamp} -->\n\n"
        f"{output}"
    )
    st.download_button(
        label="⬇️ Download Study Pack (.md)",
        data=download_content,
        file_name=download_name,
        mime="text/markdown",
    )


# ═══════════════════════════════════════════════════════════════════════════
# Generation logic
# ═══════════════════════════════════════════════════════════════════════════
if generate_clicked:
    # ── Validate input ──────────────────────────────────────────────────
    if input_error:
        st.error(f"❌ {input_error}")
    elif not validate_text(lecture_text):
        st.error("❌ Please provide some lecture notes — upload a file or paste text above.")
    else:
        try:
            model_info = get_llm_info()
        except Exception:
            model_info = {"provider": "unknown", "model": "unknown"}

        # ── Comparison mode ─────────────────────────────────────────────
        if comparison_mode:
            st.subheader("🔬 Side-by-Side Prompt Comparison")

            from concurrent.futures import ThreadPoolExecutor

            def _safe_run(ver: str):
                try:
                    return _run_generation(lecture_text, ver), None
                except Exception as exc:
                    return None, exc

            with st.spinner("🧠 Generating both V1 and V2 in parallel…"):
                with ThreadPoolExecutor(max_workers=2) as executor:
                    future1 = executor.submit(_safe_run, versions[0])
                    future2 = executor.submit(_safe_run, versions[1])
                    res1, err1 = future1.result()
                    res2, err2 = future2.result()

            # Side-by-side columns
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### V1 — Baseline")
                if err1:
                    if isinstance(err1, LLMConfigError):
                        st.error(f"❌ LLM Configuration Error:\n\n{err1}")
                    else:
                        st.error(f"❌ An error occurred with V1:\n\n{err1}")
                elif res1:
                    out1, warn1, pf1, a1 = res1
                    _display_result(out1, warn1, versions[0], pf1, model_info, a1)

            with col2:
                st.markdown("### V2 — Improved")
                if err2:
                    if isinstance(err2, LLMConfigError):
                        st.error(f"❌ LLM Configuration Error:\n\n{err2}")
                    else:
                        st.error(f"❌ An error occurred with V2:\n\n{err2}")
                elif res2:
                    out2, warn2, pf2, a2 = res2
                    _display_result(out2, warn2, versions[1], pf2, model_info, a2)

            # Structural validation comparison table
            if res1 and res2 and not err1 and not err2:
                st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                st.subheader("📊 Structural Validation Comparison")

                _, warn1, _, a1 = res1
                _, warn2, _, a2 = res2

                comp_data = {
                    "Structural Check": [
                        "3 Required Sections Present",
                        "Section Order (Summary → Terms → Questions)",
                        "No Unexpected Top-Level Sections",
                        "Exactly 5 Practice Questions",
                        "Sequential Numbering (1 to 5)",
                        "Clearly Labelled 'Answer:' for Each Question",
                        "Overall Structural Status",
                    ],
                    "V1 — Baseline": [
                        "✅ Yes" if all(a1["sections_found"].values()) else "❌ Missing",
                        "✅ Valid" if a1["sections_order_valid"] else "❌ Invalid Order",
                        "✅ None" if not a1["unexpected_sections"] else f"⚠️ {len(a1['unexpected_sections'])} extra",
                        f"✅ {a1['question_count']}/5" if a1['question_count'] == 5 else f"❌ {a1['question_count']}/5",
                        "✅ Sequential" if a1["sequential_numbering"] else "❌ Non-sequential",
                        "✅ All Labelled" if not a1["questions_missing_answers"] else f"⚠️ {len(a1['questions_missing_answers'])} missing",
                        "✅ Pass" if a1["passed_all_structural_checks"] else f"⚠️ {len(warn1)} Warning(s)",
                    ],
                    "V2 — Improved": [
                        "✅ Yes" if all(a2["sections_found"].values()) else "❌ Missing",
                        "✅ Valid" if a2["sections_order_valid"] else "❌ Invalid Order",
                        "✅ None" if not a2["unexpected_sections"] else f"⚠️ {len(a2['unexpected_sections'])} extra",
                        f"✅ {a2['question_count']}/5" if a2['question_count'] == 5 else f"❌ {a2['question_count']}/5",
                        "✅ Sequential" if a2["sequential_numbering"] else "❌ Non-sequential",
                        "✅ All Labelled" if not a2["questions_missing_answers"] else f"⚠️ {len(a2['questions_missing_answers'])} missing",
                        "✅ Pass" if a2["passed_all_structural_checks"] else f"⚠️ {len(warn2)} Warning(s)",
                    ],
                }
                st.table(comp_data)
                st.caption(
                    "⚖️ **Important Note on Evaluation**: Structural validation verifies formatting compliance only. "
                    "It does **not** verify factual correctness or establish that V2 is factually superior. "
                    "Semantic grounding must be checked against the original notes using the manual evaluation rubric."
                )

                with st.expander("📋 View Manual Grounding Review Checklist (8 Evaluation Criteria)"):
                    st.markdown(
                        "Use this 8-point rubric to evaluate the semantic quality and factual grounding of each prompt version:"
                    )
                    for item in MANUAL_GROUNDING_CHECKLIST:
                        st.markdown(f"- **{item['id']} — {item['name']}**: {item['description']}")

        # ── Single-prompt mode ──────────────────────────────────────────
        else:
            with st.spinner("🧠 Generating your study pack…"):
                try:
                    output, warnings, prompt_file, analysis = _run_generation(
                        lecture_text, selected_version
                    )
                    st.subheader("📖 Your Study Pack")
                    _display_result(
                        output, warnings, selected_version, prompt_file, model_info, analysis
                    )
                except LLMConfigError as e:
                    st.error(f"❌ LLM Configuration Error:\n\n{e}")
                except Exception as e:
                    st.error(f"❌ An error occurred while generating the study pack:\n\n{e}")
