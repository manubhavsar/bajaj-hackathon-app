import os
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage
from app.embedder import get_gemini_embeddings
from app.retriever import query_pinecone

# Load Gemini chat model once
gemini_llm = ChatVertexAI(
    model_name="gemini-1.5-flash",
    temperature=0.2,
    project=os.getenv("GCP_PROJECT_ID"),
    location=os.getenv("GCP_LOCATION"),
)

def query_documents_answer_only(question: str) -> str:
    query_embedding = get_gemini_embeddings([question])[0]
    top_chunks = query_pinecone(query_embedding, top_k=5)
    context = "\n\n".join([chunk["text"] for chunk in top_chunks])

    prompt = f"""
You are a document assistant. Extract concise, clear, and well-structured answers from the provided document chunks.

--- CONTEXT ---
{context}
--- END CONTEXT ---

QUESTION: "{question}"

RULES:
- Answer in a concise and formal tone, limiting each response to 1–2 sentences.
- Avoid repeating unnecessary policy conditions.
- Do not explain how premiums or discounts are calculated unless asked.
- Avoid legal disclaimers or background details.
- If the answer is not in the text, say: "The answer is not available in the document."
"""



    response = gemini_llm.invoke([HumanMessage(content=prompt)])
    return response.content.strip()