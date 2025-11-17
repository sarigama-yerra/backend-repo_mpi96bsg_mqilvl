import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from database import db, create_document, get_documents
from schemas import Document, Clause, Policy, Comment, Message, Thread, User
from datetime import datetime

app = FastAPI(title="Legal AI Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Legal AI Assistant Backend Running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        from database import db as _db
        if _db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = _db.name if hasattr(_db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                response["collections"] = _db.list_collection_names()
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response

# Basic models for requests
class AnalyzeRequest(BaseModel):
    document_id: str

class ChatRequest(BaseModel):
    query: str

# Upload endpoint (stores metadata, not file storage implementation)
@app.post("/documents", response_model=dict)
async def upload_document(file: UploadFile = File(...), uploader_email: str = "unknown@example.com"):
    if not file.filename.lower().endswith((".docx", ".doc")):
        raise HTTPException(status_code=400, detail="Only Word documents are supported (.docx/.doc)")

    doc = Document(title=file.filename, filename=file.filename, uploader_email=uploader_email)
    inserted_id = create_document("document", doc)
    return {"document_id": inserted_id, "status": "uploaded"}

# List documents
@app.get("/documents")
def list_documents():
    docs = get_documents("document", limit=50)
    # Convert ObjectId to str if present
    for d in docs:
        if "_id" in d:
            d["_id"] = str(d["_id"])
    return {"items": docs}

# Dummy analyze endpoint (placeholder for Gemini + RAG integration)
@app.post("/analyze")
async def analyze_contract(req: AnalyzeRequest):
    # Here you would: fetch document text, chunk, embed into Chroma, query Gemini 2.5 Flash, etc.
    # For now, we return a mocked structure for UI wiring.
    sample_clauses = [
        Clause(document_id=req.document_id, clause_type="liability", text="Limitation of liability is capped at fees paid.", risk="medium", policy_refs=["Policy-LIAB-1"]).model_dump(),
        Clause(document_id=req.document_id, clause_type="ip", text="All IP remains with the supplier.", risk="high", policy_refs=["Policy-IP-2"]).model_dump(),
        Clause(document_id=req.document_id, clause_type="payment", text="Net 60 payment terms.", risk="low", policy_refs=["Policy-PAY-3"]).model_dump(),
    ]
    return {
        "document_id": req.document_id,
        "summary_risk": "medium",
        "clauses": sample_clauses,
        "redlines": [
            {"range": [10, 45], "suggestion": "Change liability cap to 12 months of fees", "policy": "Policy-LIAB-1"}
        ]
    }

# Simple policy chatbot mock
@app.post("/chat")
async def policy_chat(req: ChatRequest):
    return {"answer": f"This is a placeholder answer for: '{req.query}'. In production, this would query your policy knowledge base with RAG."}

# Negotiation threads
@app.post("/threads")
def create_thread(thread: Thread):
    inserted_id = create_document("thread", thread)
    return {"thread_id": inserted_id}

@app.get("/threads")
def list_threads():
    ths = get_documents("thread", limit=50)
    for t in ths:
        t["_id"] = str(t["_id"])
    return {"items": ths}

@app.post("/messages")
def post_message(msg: Message):
    inserted_id = create_document("message", msg)
    return {"message_id": inserted_id}

@app.get("/messages")
def get_messages(thread_id: Optional[str] = None):
    filt = {"thread_id": thread_id} if thread_id else {}
    msgs = get_documents("message", filter_dict=filt, limit=200)
    for m in msgs:
        m["_id"] = str(m["_id"])
    return {"items": msgs}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
