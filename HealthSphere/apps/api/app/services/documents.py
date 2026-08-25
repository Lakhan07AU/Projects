"""Document validation and text extraction.

- Validates magic bytes (never trust the client-supplied content type).
- PDFs: extract embedded text with pypdf.
- Images: OCR requires an external engine; when unavailable we return no text
  and the pipeline asks the user to verify/enter values manually. We never
  fabricate values from unreadable documents.
"""
import logging
from io import BytesIO

logger = logging.getLogger("healthsphere.docs")

ALLOWED_MIME = {"application/pdf", "image/jpeg", "image/png"}


class DocumentValidationError(Exception):
    pass


def validate_file(content: bytes, declared_mime: str, max_size_mb: int) -> str:
    """Validate size + real file type via magic bytes. Returns actual mime."""
    if not content:
        raise DocumentValidationError("The uploaded file is empty.")
    if len(content) > max_size_mb * 1024 * 1024:
        raise DocumentValidationError(f"File exceeds the maximum size of {max_size_mb} MB.")

    mime = None
    if content[:5] == b"%PDF-":
        mime = "application/pdf"
    elif content[:3] == b"\xff\xd8\xff":
        mime = "image/jpeg"
    elif content[:8] == b"\x89PNG\r\n\x1a\n":
        mime = "image/png"
    if mime is None or mime not in ALLOWED_MIME:
        raise DocumentValidationError(
            "Unsupported file type. Please upload a PDF, JPG, or PNG medical report."
        )
    return mime


def extract_text(content: bytes, mime: str) -> tuple[str | None, bool]:
    """Return (text, needs_ocr). needs_ocr=True means we couldn't read it."""
    if mime == "application/pdf":
        try:
            from pypdf import PdfReader

            reader = PdfReader(BytesIO(content))
            pages = [(page.extract_text() or "") for page in reader.pages]
            text = "\n".join(pages).strip()
            if len(text) >= 40:  # enough signal to process
                return text, False
            return None, True
        except Exception:
            logger.exception("PDF text extraction failed")
            return None, True
    # Images require an OCR engine which is not configured in this deployment.
    return None, True


def pdf_page_count(content: bytes) -> int:
    try:
        from pypdf import PdfReader

        return len(PdfReader(BytesIO(content)).pages)
    except Exception:
        return 1
