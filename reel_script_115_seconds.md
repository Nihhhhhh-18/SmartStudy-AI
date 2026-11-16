# 🎬 SmartStudy AI — Milestone 2 Demo Reel Script
**Target Duration:** ~115 seconds (Allowed: 90 – 150 seconds)  
**Format:** Screen recording of your Streamlit app / VS Code with voiceover or captions.

---

### Part 1: Problem Definition (~10 seconds)
*(On Screen: Show the Streamlit header `📚 SmartStudy AI` and a messy, unstructured text file of lecture notes)*

> **Speaker:**  
> "Hey everyone! For our Prompt Engineering project—Problem C2—we built **SmartStudy AI**. University students often get overwhelmed revising from dense, unstructured lecture slides. General chatbots often hallucinate, bring in outside syllabus concepts, or produce inconsistent practice questions. SmartStudy AI solves this by transforming raw lecture notes into guaranteed source-grounded study packs."

---

### Part 2: Prompt Experimentation & Comparison (~35 seconds)
*(On Screen: Toggle on **🔬 Comparison mode** in the sidebar. Show V1 on the left and V2 on the right, or zoom in on the prompt templates in VS Code / UI)*

> **Speaker:**  
> "Here in our sidebar, we've implemented an empirical prompt comparison engine.  
> In our initial **Baseline Prompt V1**, when we asked for key terms, the LLM hallucinated external definitions for terms like *dropout* and *pruning* that weren't defined in the notes, scored only 50% on our rubric, and dumped answers into an extra fourth section.  
> In our **Production Prompt V2**, we introduced strict negative grounding constraints, a deterministic fallback sentence—*‘The supplied notes do not define this term in detail’*—and a 5-tier Bloom's taxonomy question structure. This jumped our evaluation score to a perfect 100% with zero structural errors!"

---

### Part 3: Live Working Demonstration (~45 seconds)
*(On Screen: Click **🚀 Generate Study Pack** in Streamlit. Show the progress spinner, then show the real-time generated output with the green validation badge: `✅ All structural checks passed`)*

> **Speaker:**  
> "Let's run a live demo with our Machine Learning lecture notes.  
> As the model generates, our built-in 10-point structural validator immediately inspects the output.  
> Notice the green badge: all three required sections are present in exact order:  
> First, a clear, grounded **Summary**.  
> Second, **Key Terms & Definitions**—notice how terms without full definitions trigger our canonical fallback without hallucinating!  
> Third, exactly **5 sequentially numbered practice questions**: multiple-choice with distractors, short-answer, fill-in-the-blank, a scenario-based question, and true/false with correction.  
> Finally, the student can click **Download Study Pack** to export reproducible Markdown with model metadata."

---

### Part 4: Progress & Next Steps for Milestone 3 (~20 seconds)
*(On Screen: Show the terminal with `56 passed in 1.15s` from running `pytest tests/`, then show your repository folder)*

> **Speaker:**  
> "For Milestone 2, all five core modules are fully working, backed by 56 automated unit tests.  
> Moving into Milestone 3, we plan to implement a RAG chunking pipeline for full textbooks, add an OCR pre-processor for scanned handwritten notes, and integrate an upfront academic content filter.  
> Thank you!"

---

### 💡 Recording Checklist Before You Submit:
- [ ] Keep total recording time between **90 and 150 seconds** (115s is the sweet spot).
- [ ] Set your Google Drive or YouTube video to **"Anyone with the link can view"** (no login required).
- [ ] Record a real live run of the app—do not use static mockup slides.

