"""
tests/test_document_loader.py — Unit tests for the document loader module.

These tests run without an API key — they only test local text
and PDF extraction logic.
"""

import os
import pytest
import pymupdf  # PyMuPDF — used to create test PDFs in memory

from src.document_loader import (
    extract_text_from_txt,
    extract_text_from_pdf,
    validate_text,
    load_document,
)


# ═══════════════════════════════════════════════════════════════════════════
# TXT extraction
# ═══════════════════════════════════════════════════════════════════════════

class TestExtractTextFromTxt:
    def test_utf8_text(self):
        raw = "Hello, world! Ünîcödé.".encode("utf-8")
        assert extract_text_from_txt(raw) == "Hello, world! Ünîcödé."

    def test_ascii_text(self):
        raw = b"Plain ASCII text."
        assert extract_text_from_txt(raw) == "Plain ASCII text."

    def test_latin1_fallback(self):
        # \xe9 is 'é' in latin-1 but invalid standalone UTF-8
        raw = b"Caf\xe9"
        result = extract_text_from_txt(raw)
        assert "Caf" in result  # should not crash

    def test_empty_bytes(self):
        assert extract_text_from_txt(b"") == ""


# ═══════════════════════════════════════════════════════════════════════════
# PDF extraction
# ═══════════════════════════════════════════════════════════════════════════

def _create_test_pdf(text: str) -> bytes:
    """Create a simple single-page PDF with the given text, return bytes."""
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 72), text, fontsize=12)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def _create_empty_pdf() -> bytes:
    """Create a PDF with one blank page (no text)."""
    doc = pymupdf.open()
    doc.new_page()
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


class TestExtractTextFromPdf:
    def test_single_page_pdf(self):
        pdf_bytes = _create_test_pdf("Overfitting occurs when a model learns too closely.")
        text = extract_text_from_pdf(pdf_bytes)
        assert "Overfitting" in text

    def test_empty_pdf(self):
        pdf_bytes = _create_empty_pdf()
        text = extract_text_from_pdf(pdf_bytes)
        # Should return empty (or whitespace-only) text
        assert not text.strip()


# ═══════════════════════════════════════════════════════════════════════════
# validate_text
# ═══════════════════════════════════════════════════════════════════════════

class TestValidateText:
    def test_valid_text(self):
        assert validate_text("Some content.") is True

    def test_empty_string(self):
        assert validate_text("") is False

    def test_whitespace_only(self):
        assert validate_text("   \n\t  ") is False

    def test_none(self):
        assert validate_text(None) is False  # type: ignore[arg-type]


# ═══════════════════════════════════════════════════════════════════════════
# load_document (integration-level)
# ═══════════════════════════════════════════════════════════════════════════

class TestLoadDocument:
    def test_load_txt_file(self):
        text, err = load_document("notes.txt", b"Hello from a TXT file.")
        assert err is None
        assert "Hello" in text

    def test_load_pdf_file(self):
        pdf_bytes = _create_test_pdf("Regularization reduces overfitting.")
        text, err = load_document("lecture.pdf", pdf_bytes)
        assert err is None
        assert "Regularization" in text

    def test_empty_txt(self):
        text, err = load_document("empty.txt", b"")
        assert err is not None
        assert "empty" in err.lower()

    def test_empty_pdf(self):
        pdf_bytes = _create_empty_pdf()
        text, err = load_document("blank.pdf", pdf_bytes)
        assert err is not None
        assert "OCR" in err or "image" in err.lower() or "text" in err.lower()

    def test_unsupported_extension(self):
        text, err = load_document("notes.docx", b"some data")
        assert err is not None
        assert "Unsupported" in err
