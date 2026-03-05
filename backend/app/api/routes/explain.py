"""RAG + LLM explanation API routes."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any
from app.services.llm_service import generate_explanation
from app.llm_engine.ollama_client import check_ollama_health
from app.rag_engine.embedder import load_knowledge_base

router = APIRouter()


class ExplainRequest(BaseModel):
    anomaly_rows: list[dict[str, Any]]
    anomaly_count: int
    anomaly_ratio: float


class ExplainResponse(BaseModel):
    attack_type: str | None = None
    severity: str | None = None
    confidence: str | None = None
    explanation: str | None = None
    owasp_category: str | None = None
    indicators: list[str] | None = None
    recommended_fix: str | None = None
    references: list[str] | None = None
    risk_level: str | None = None
    summary: str | None = None
    immediate_action: str | None = None
    rag_context_used: str | None = None
    parse_error: bool | None = None
    raw_response: str | None = None


@router.post("/", response_model=ExplainResponse)
def explain_anomalies(request: ExplainRequest):
    """
    Generate AI-powered security explanation for detected anomalies.
    Uses RAG retrieval + Ollama LLM to produce structured intelligence.
    Requires Ollama to be running locally.
    """
    if not request.anomaly_rows:
        raise HTTPException(status_code=400, detail="anomaly_rows cannot be empty.")

    try:
        result = generate_explanation(
            anomaly_rows=request.anomaly_rows,
            anomaly_count=request.anomaly_count,
            anomaly_ratio=request.anomaly_ratio,
        )
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/health")
def ollama_health():
    """Check Ollama server and model availability."""
    return check_ollama_health()


@router.post("/reload-kb")
def reload_knowledge_base():
    """Force reload the OWASP knowledge base into ChromaDB."""
    count = load_knowledge_base(force_reload=True)
    return {"message": f"Knowledge base reloaded with {count} documents."}
