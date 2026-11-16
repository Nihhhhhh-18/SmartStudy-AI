"""
document_loader.py — Extract text from uploaded files (PDF or TXT).

Supports:
- TXT files: read as UTF-8 with graceful fallback.
- PDF files: extract text from every page using PyMuPDF (fitz).
- Pasted text: returned as-is after whitespace validation.
"""

try:
    import pymupdf  # Modern import name
except ImportError:
    import fitz as pymupdf  # Legacy import name


def extract_text_from_txt(file_bytes: bytes) -> str:
    """
    Decode bytes from a TXT file into a string.

    Tries UTF-8 first, then falls back to latin-1 so that
    files with unusual encodings do not crash the application.
    """
    try:
        text = file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        # latin-1 can decode any byte sequence without errors
        text = file_bytes.decode("latin-1")
    return text


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text from every page of a PDF using PyMuPDF.

    Returns the combined text from all pages.
    If no extractable text is found (e.g. image-only PDF), returns an
    empty string so the caller can show a helpful message.
    """
    text_parts: list[str] = []
    # Open the PDF from in-memory bytes
    with pymupdf.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            page_text = page.get_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def validate_text(text: str) -> bool:
    """
    Return True if *text* contains at least some non-whitespace content.
    """
    return bool(text and text.strip())


def load_document(file_name: str, file_bytes: bytes) -> tuple[str, str | None]:
    """
    High-level helper: choose the right extractor based on file extension.

    Returns
    -------
    (text, error_message)
        text : the extracted text (may be empty on failure)
        error_message : a user-friendly error string, or None on success
    """
    name_lower = file_name.lower()

    if name_lower.endswith(".txt"):
        text = extract_text_from_txt(file_bytes)
    elif name_lower.endswith(".pdf"):
        text = extract_text_from_pdf(file_bytes)
    else:
        return "", f"Unsupported file type: {file_name}. Please upload a PDF or TXT file."

    if not validate_text(text):
        if name_lower.endswith(".pdf"):
            return "", (
                "No extractable text was found in this PDF. "
                "It may contain only images or scanned pages. "
                "OCR is not supported in this version — please provide "
                "a text-based PDF or paste your notes directly."
            )
        return "", "The uploaded file appears to be empty."

    return text, None
