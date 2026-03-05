import axiosClient from "./axiosClient";
import type { ExplainPayload, ExplainResponse } from "../types/insights";

export async function generateInsights(payload: ExplainPayload): Promise<ExplainResponse> {
  const response = await axiosClient.post<ExplainResponse>("/explain/", payload, {
    timeout: 180000, // 3 minutes for LLM
  });
  return response.data;
}
