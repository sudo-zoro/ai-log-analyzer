import axiosClient from "./axiosClient";
import type { DetectionRun, RunDetectionPayload } from "../types/detection";

export async function runDetection(payload: RunDetectionPayload): Promise<DetectionRun> {
  const formData = new FormData();
  formData.append("model_id", payload.model_id);
  formData.append("file", payload.file);

  const response = await axiosClient.post<DetectionRun>("/detect/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

  return response.data;
}
