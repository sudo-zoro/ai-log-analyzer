import { useMutation } from "@tanstack/react-query";
import { runDetection } from "../api/detectionApi";
import type { RunDetectionPayload } from "../types/detection";

export function useRunDetection() {
  return useMutation({
    mutationFn: (payload: RunDetectionPayload) => runDetection(payload),
  });
}
