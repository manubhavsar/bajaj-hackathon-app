import hashlib
import json
import os

CACHE_FILE = "embedding_cache.json"

# Load existing cache if available
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        EMBEDDING_CACHE = json.load(f)
else:
    EMBEDDING_CACHE = {}

def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def get_cached_embedding(text: str):
    key = hash_text(text)
    return EMBEDDING_CACHE.get(key)

def set_cached_embedding(text: str, embedding: list):
    key = hash_text(text)
    EMBEDDING_CACHE[key] = embedding
    with open(CACHE_FILE, "w") as f:
        json.dump(EMBEDDING_CACHE, f)
