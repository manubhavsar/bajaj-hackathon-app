# app/ingestion/chunker.py
from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_text(text: str, chunk_size=1000, chunk_overlap=200):
    splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150,
    separators=["\n\n", "\n", ".", " ", ""],
    )
    chunks = splitter.split_text(text)
    return [{"text": chunk} for chunk in chunks]  # 🟢 Now each chunk is a dict