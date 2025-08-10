import os
from typing import List
from dotenv import load_dotenv
from pinecone import Pinecone
from app.embedder import get_gemini_embeddings

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = os.getenv("PINECONE_INDEX")

if not index_name:
    raise ValueError("PINECONE_INDEX not set.")
if index_name not in pc.list_indexes().names():
    raise ValueError(f"Index '{index_name}' not found.")

index = pc.Index(index_name)

def upsert_chunks(chunks: List[dict]) -> None:
    if not chunks:
        return

    ids = [chunk["id"] for chunk in chunks]
    texts = [chunk["text"] for chunk in chunks]
    metas = [chunk["metadata"] for chunk in chunks]

    for i in range(len(metas)):
        metas[i]["text"] = texts[i]

    vectors = get_gemini_embeddings(texts)

    if any(len(vec) != 3072 for vec in vectors):
        raise ValueError("Vector dimension mismatch! Expected 3072.")

    payload = [(ids[i], vectors[i], metas[i]) for i in range(len(chunks))]
    index.upsert(vectors=payload)

def query_pinecone(query_embedding: List[float], top_k: int = 4) -> List[dict]:
    response = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )

    print("Query Results:")
    for match in response["matches"]:
        print(match["score"], match["metadata"].get("text", "")[:100])

    return [
        {
            "score": match["score"],
            "text": match["metadata"].get("text", ""),
            "metadata": match["metadata"]
        }
        for match in response["matches"]
    ]