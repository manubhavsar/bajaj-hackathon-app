# app/models/document.py
from pydantic import BaseModel
from typing import List

class ChunkMetadata(BaseModel):
    file_name: str
    chunk_index: int

class DocumentChunk(BaseModel):
    content: str
    metadata: ChunkMetadata
