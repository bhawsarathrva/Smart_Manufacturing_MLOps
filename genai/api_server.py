import os
import uuid
from typing import Optional, Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn

from chatbot import ManufacturingChatbot
from rag_engine import RAGEngine

# ─── App Setup ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Smart Manufacturing API",
    description="AI-powered Chatbot + RAG for Smart Manufacturing",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global chatbot instance
chatbot = ManufacturingChatbot()


# ─── Pydantic Models ───────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    intent: str
    sources: list
    session_id: str
    message_count: int
    timestamp: str

class RAGQueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

class RAGQueryResponse(BaseModel):
    answer: str
    sources: list
    retrieved_chunks: int
    confidence: int
    timestamp: str

class MetricsUpdateRequest(BaseModel):
    metrics: Dict[str, Any]

class InitResponse(BaseModel):
    status: str
    message: str
    timestamp: str


# ─── Startup ───────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    """Initialize chatbot on server startup."""
    print("🚀 Initializing Manufacturing GenAI module...")
    chatbot.initialize()
    print("✅ GenAI module ready!")


# ─── Health Check ──────────────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Smart Manufacturing GenAI API",
        "timestamp": datetime.now().isoformat(),
        "openai_model": "gpt-4o-mini",
        "rag_initialized": chatbot._initialized
    }


# ─── Chat Endpoints ────────────────────────────────────────────────────────────

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint. Send a message and receive an AI response.
    Creates a new session if session_id is not provided.
    """
    session_id = request.session_id or str(uuid.uuid4())

    try:
        result = chatbot.chat(
            message=request.message,
            session_id=session_id
        )
        return ChatResponse(
            response=result["response"],
            intent=result["intent"],
            sources=result["sources"],
            session_id=session_id,
            message_count=result["message_count"],
            timestamp=result["timestamp"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@app.get("/chat/session/{session_id}")
async def get_session(session_id: str):
    """Retrieve conversation history for a session."""
    summary = chatbot.get_session_summary(session_id)
    if "error" in summary:
        raise HTTPException(status_code=404, detail=summary["error"])
    return summary


@app.delete("/chat/session/{session_id}")
async def clear_session(session_id: str):
    """Clear conversation history for a session."""
    chatbot.clear_session(session_id)
    return {"status": "cleared", "session_id": session_id}


# ─── RAG Endpoints ─────────────────────────────────────────────────────────────

@app.post("/rag/query", response_model=RAGQueryResponse)
async def rag_query(request: RAGQueryRequest):
    """
    Direct RAG query without conversational context.
    Good for single-shot Q&A about manufacturing knowledge.
    """
    try:
        result = chatbot.rag_engine.query(request.query)
        return RAGQueryResponse(
            answer=result["answer"],
            sources=result["sources"],
            retrieved_chunks=result["retrieved_chunks"],
            confidence=result["confidence"],
            timestamp=result["timestamp"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG error: {str(e)}")


@app.post("/rag/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document (PDF text, SOP, maintenance manual) to enrich the RAG knowledge base.
    Supports .txt files. For PDFs, extract text first using PyMuPDF.
    """
    content = await file.read()
    text = content.decode("utf-8", errors="ignore")

    if len(text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Document too short or empty")

    message = chatbot.add_document_to_knowledge_base(text, file.filename)
    return {"status": "success", "message": message, "filename": file.filename}


# ─── Metrics Integration ────────────────────────────────────────────────────────

@app.post("/metrics/update")
async def update_metrics(request: MetricsUpdateRequest):
    """
    Push fresh live metrics into the RAG vector store.
    Call this from your MLOps pipeline when metrics update.
    """
    try:
        chatbot.rag_engine.update_live_metrics(request.metrics)
        return {"status": "updated", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Suggested Questions Endpoint ──────────────────────────────────────────────

@app.get("/chat/suggestions")
async def get_suggestions():
    """Return suggested questions for the chat UI."""
    return {
        "suggestions": [
            "What anomalies were detected in the last 24 hours?",
            "Which machines need maintenance soon?",
            "What is the current OEE and how can I improve it?",
            "Explain the warning alert on CNC-03",
            "Which ML models are underperforming?",
            "How can I reduce energy consumption?",
            "What does a vibration spike above 7.1 mm/s mean?",
            "Show me today's production summary",
        ]
    }


# ─── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8001,   # Use 8001 to avoid conflict with existing backend on 8000
        reload=True,
        log_level="info"
    )