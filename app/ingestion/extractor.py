# app/ingestion/extractor.py
import fitz  # PyMuPDF
import docx
import email
from email import policy
from email.parser import BytesParser
from pathlib import Path

def extract_text_from_pdf(file_path: Path) -> str:
    text = ""
    doc = fitz.open(str(file_path))
    for page in doc:
        text += page.get_text()
    return text

def extract_text_from_docx(file_path: Path) -> str:
    doc = docx.Document(str(file_path))
    return "\n".join(p.text for p in doc.paragraphs)

def extract_text_from_eml(file_path: Path) -> str:
    with open(file_path, "rb") as f:
        msg = BytesParser(policy=policy.default).parse(f)
    return msg.get_body(preferencelist=('plain')).get_content()

def extract_text(file_path: str, filename: str) -> str:
    ext = filename.lower().split(".")[-1]
    if ext == "pdf":
        return extract_text_from_pdf(file_path)
    elif ext == "docx":
        return extract_text_from_docx(file_path)
    elif ext == "eml":
        return extract_text_from_eml(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")