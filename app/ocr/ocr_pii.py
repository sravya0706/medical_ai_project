"""
Real OCR (Tesseract via pytesseract) + regex-based PII redaction —
matches Module 7 exactly.
"""
import re
from io import BytesIO
import pytesseract
from PIL import Image

# --- OCR ---

def extract_text_from_image(image_path: str) -> str:
    image = Image.open(image_path)
    return pytesseract.image_to_string(image)


def extract_text_from_image_bytes(image_bytes: bytes) -> str:
    """Extract OCR text from an uploaded image without writing it to disk."""
    with Image.open(BytesIO(image_bytes)) as image:
        return pytesseract.image_to_string(image)


# --- PII Redaction ---
# HONESTY NOTE (matches the documented limitation exactly): regex only
# catches structurally predictable fields. Patient names have no fixed
# pattern, so this cannot reliably redact them — a production system needs
# a proper NER model (e.g. Microsoft Presidio) layered on top. Documented
# here, not hidden.

PHONE_PATTERN = re.compile(r"\b\d{10}\b")
AADHAAR_LIKE_PATTERN = re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b")
EMAIL_PATTERN = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")


def redact_pii(text: str) -> str:
    text = PHONE_PATTERN.sub("[REDACTED_PHONE]", text)
    text = AADHAAR_LIKE_PATTERN.sub("[REDACTED_ID]", text)
    text = EMAIL_PATTERN.sub("[REDACTED_EMAIL]", text)
    return text


def process_document(image_path: str) -> dict:
    raw_text = extract_text_from_image(image_path)
    redacted_text = redact_pii(raw_text)
    return {"raw_text": raw_text, "redacted_text": redacted_text}


def process_document_bytes(image_bytes: bytes) -> str:
    """Return only redacted OCR text for the request pipeline.

    Raw OCR text can contain patient data, so callers that send content to
    retrieval or an LLM must use this function rather than passing raw text
    downstream.
    """
    return redact_pii(extract_text_from_image_bytes(image_bytes))


if __name__ == "__main__":
    # PII redaction smoke test (no image needed for this part)
    sample = "Patient: John Doe, Phone: 9876543210, ID: 1234 5678 9012, Email: john@example.com. Hemoglobin: 11.2 g/dL."
    print(redact_pii(sample))
