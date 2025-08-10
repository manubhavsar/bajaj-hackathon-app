# ingest_local.py

from pathlib import Path
from app.ingestion.extractor import extract_text_from_pdf
from app.ingestion.chunker import chunk_text
from app.retriever import upsert_chunks

def ingest_file_from_path(filepath: str):
    path = Path(filepath)
    text = extract_text_from_pdf(path)

    chunks = chunk_text(text)
    chunk_objs = [
        {
            "id": f"{path.name}-{i}",
            "text": chunk,
            "metadata": {"file_name": path.name, "chunk_index": i}
        }
        for i, chunk in enumerate(chunks)
    ]

    upsert_chunks(chunk_objs)
    print(f"✅ Ingested {len(chunks)} chunks from {path.name}")

if __name__ == "__main__":
    ingest_file_from_path("/Users/manu/Desktop/Bajaj-RAG/BAJAJ PDF 1.pdf")  # <-- change this path