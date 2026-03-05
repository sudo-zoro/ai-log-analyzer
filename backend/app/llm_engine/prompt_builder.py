"""
Prompt Builder — constructs structured prompts for LLM security analysis.
"""


SYSTEM_PROMPT = """You are SecRAG, an expert cybersecurity analyst AI. 
You analyze anomalous system log entries and provide structured security intelligence.
Always respond in valid JSON format only. Be concise, precise, and actionable.
Base your analysis on the provided security context and log data."""


def build_analysis_prompt(
    anomaly_rows: list[dict],
    rag_context: str,
    model_name: str = "",
) -> str:
    """
    Build the main analysis prompt for anomaly explanation.

    anomaly_rows: list of raw log row dicts (the anomalous rows)
    rag_context:  retrieved OWASP/security knowledge
    """
    # Format log samples (limit to top 5 to keep prompt manageable)
    log_samples = anomaly_rows[:5]
    log_text = "\n".join(
        f"  Row {i+1}: {row}" for i, row in enumerate(log_samples)
    )

    prompt = f"""You are analyzing anomalous log entries detected by an Isolation Forest model.

## Security Context (from OWASP & Security Knowledge Base)
{rag_context}

## Detected Anomalous Log Entries ({len(anomaly_rows)} total anomalies, showing top {len(log_samples)})
{log_text}

## Your Task
Analyze these anomalous log entries in the context of the security knowledge provided.
Return a JSON object with EXACTLY this structure:

{{
  "attack_type": "short name of most likely attack type",
  "severity": "Critical | High | Medium | Low",
  "confidence": "High | Medium | Low",
  "explanation": "2-3 sentence explanation of what the anomalies indicate",
  "owasp_category": "OWASP category if applicable, or null",
  "indicators": ["list", "of", "key", "log", "indicators"],
  "recommended_fix": "Specific actionable remediation steps",
  "references": ["OWASP link or security reference if applicable"]
}}

Respond with ONLY the JSON object. No markdown, no explanation outside the JSON."""

    return prompt


def build_summary_prompt(anomaly_count: int, anomaly_ratio: float) -> str:
    """Build a brief prompt for a high-level summary of detection results."""
    return f"""Summarize the security risk for a log analysis where:
- Total anomaly count: {anomaly_count}
- Anomaly ratio: {anomaly_ratio:.1%} of all log entries

Respond with a single JSON object:
{{
  "risk_level": "Critical | High | Medium | Low | Info",
  "summary": "One sentence risk summary",
  "immediate_action": "Most important action to take right now"
}}

Respond with ONLY the JSON."""
