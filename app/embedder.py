import os
from dotenv import load_dotenv
from google.cloud import aiplatform
from google.oauth2 import service_account
from langchain_google_vertexai import VertexAIEmbeddings

load_dotenv()


# Load credentials from the secure path set in GOOGLE_APPLICATION_CREDENTIALS
credentials = service_account.Credentials.from_service_account_file(
    os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
)

aiplatform.init(
    project=os.getenv("GCP_PROJECT_ID"),
    location=os.getenv("GCP_LOCATION"),
    credentials=credentials
)


embedding_model = VertexAIEmbeddings(
    model_name="gemini-embedding-001",
    project=os.getenv("GCP_PROJECT_ID"),
    location=os.getenv("GCP_LOCATION"),
)

def get_gemini_embeddings(texts: list[str]) -> list[list[float]]:
    raw = embedding_model.embed_documents(texts)
    if isinstance(raw, list) and isinstance(raw[0], dict) and "embedding" in raw[0]:
        return [r["embedding"] for r in raw]
    return raw

def embed_chunks(chunks: list[dict]) -> None:
    texts = [chunk["text"] for chunk in chunks]
    vectors = get_gemini_embeddings(texts)
    for i, chunk in enumerate(chunks):
        chunk["embedding"] = vectors[i]