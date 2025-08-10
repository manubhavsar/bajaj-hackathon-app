from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import tempfile
import requests
import os
import asyncio
import uuid

from app.ingestion.extractor import extract_text
from app.ingestion.chunker import chunk_text
from app.models.document import ChunkMetadata, DocumentChunk
from app.embedder import embed_chunks
from app.retriever import upsert_chunks
from app.query_engine import query_documents_answer_only 
# -------------------- FastAPI Setup --------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

AUTHORIZED_TOKENS = {"680f333f3b6e36d20c0bcfe99ac261f944087fad3c240071d12c1bd2eff4b62a"}
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if token not in AUTHORIZED_TOKENS:
        raise HTTPException(status_code=403, detail="Unauthorized token")


# -------------------- File Ingestion Endpoint --------------------
@app.post("/ingest")
async def ingest_file(file: UploadFile = File(...)):
    file_path = os.path.join(tempfile.gettempdir(), file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    text = extract_text(file_path, file.filename)
    chunks = chunk_text(text)

    for chunk in chunks:
        chunk["id"] = str(uuid.uuid4())
        chunk["metadata"] = {
            "source": file.filename,
            "type": "upload"
        }

    embed_chunks(chunks)
    upsert_chunks(chunks)

    return {"message": "File ingested successfully", "chunks": len(chunks)}


# -------------------- Multi-Question RAG Endpoint --------------------
class RunRequest(BaseModel):
    documents: str
    questions: list[str]

@app.post("/hackrx/run")
async def run_rag(
    body: RunRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    verify_token(credentials)

    # Download file
    response = requests.get(body.documents)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to download document")

    filename = body.documents.split("/")[-1].split("?")[0]
    file_path = os.path.join(tempfile.gettempdir(), filename)
    with open(file_path, "wb") as f:
        f.write(response.content)

    # Extract, chunk, embed, upsert
    text = extract_text(file_path, filename)
    chunks = chunk_text(text)

    for chunk in chunks:
        chunk["id"] = str(uuid.uuid4())
        chunk["metadata"] = {
            "source": filename,
            "type": "web"
        }

    embed_chunks(chunks)
    upsert_chunks(chunks)

    # 🔄 Parallel processing of questions
    tasks = [query_documents_answer_only(question) for question in body.questions]
    answers = await asyncio.gather(*tasks)

    return {"answers": answers}

@app.get("/")
def root():
    return {"message": "Bajaj Hackathon App is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=False)