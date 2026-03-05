import { useMutation } from "@tanstack/react-query";
import { generateInsights } from "../api/insightsApi";
import type { ExplainPayload } from "../types/insights";

export function useInsights() {
  return useMutation({
    mutationFn: (payload: ExplainPayload) => generateInsights(payload),
  });
}
