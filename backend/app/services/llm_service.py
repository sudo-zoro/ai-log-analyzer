"""
LLM Service — orchestrates RAG retrieval + Ollama inference to produce
structured security explanations for detected anomalies.
"""
import json
import re
from app.rag_engine.embedder import retrieve_context
from app.llm_engine.ollama_client import call_ollama
from app.llm_engine.prompt_builder import (
    SYSTEM_PROMPT,
    build_analysis_prompt,
    build_summary_prompt,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


def _extract_json(text: str) -> dict:
    """Extract the first JSON object from LLM output (handle markdown fences)."""
    # Strip markdown code fences if present
    text = re.sub(r"```(?:json)?", "", text).strip()

    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find JSON block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    logger.warning("Could not parse JSON from LLM output. Returning raw text.")
    return {"raw_response": text, "parse_error": True}


def generate_explanation(
    anomaly_rows: list[dict],
    anomaly_count: int,
    anomaly_ratio: float,
) -> dict:
    """
    Full RAG + LLM pipeline:
    1. Build a query from anomaly data
    2. Retrieve relevant security context from ChromaDB
    3. Build prompt with context + log samples
    4. Call Ollama for structured analysis
    5. Parse and return JSON response

    Returns a dict with keys:
        attack_type, severity, confidence, explanation,
        owasp_category, indicators, recommended_fix, references,
        risk_level, summary, immediate_action, rag_context_used
    """
    # Build retrieval query from anomaly rows
    query_parts = []
    for row in anomaly_rows[:3]:
        query_parts.append(" ".join(str(v) for v in row.values() if v))
    query = " ".join(query_parts)[:500]  # cap query length

    logger.info("Retrieving RAG context for query: %s...", query[:80])
    rag_context = retrieve_context(query, n_results=4)

    # --- Main analysis ---
    analysis_prompt = build_analysis_prompt(
        anomaly_rows=anomaly_rows,
        rag_context=rag_context,
    )

    logger.info("Calling Ollama for anomaly analysis (%d anomalies)...", anomaly_count)
    raw_analysis = call_ollama(prompt=analysis_prompt, system_prompt=SYSTEM_PROMPT)
    analysis = _extract_json(raw_analysis)

    # --- Summary ---
    summary_prompt = build_summary_prompt(anomaly_count, anomaly_ratio)
    raw_summary = call_ollama(prompt=summary_prompt, system_prompt=SYSTEM_PROMPT)
    summary = _extract_json(raw_summary)

    return {
        **analysis,
        **summary,
        "rag_context_used": rag_context[:1000],   # truncated for API response
    }
