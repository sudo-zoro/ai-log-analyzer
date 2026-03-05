export type ExplainPayload = {
  anomaly_rows: Record<string, string>[];
  anomaly_count: number;
  anomaly_ratio: number;
};

export type ExplainResponse = {
  attack_type: string | null;
  severity: string | null;
  confidence: string | null;
  explanation: string | null;
  owasp_category: string | null;
  indicators: string[] | null;
  recommended_fix: string | null;
  references: string[] | null;
  risk_level: string | null;
  summary: string | null;
  immediate_action: string | null;
  rag_context_used: string | null;
  parse_error: boolean | null;
  raw_response: string | null;
};
