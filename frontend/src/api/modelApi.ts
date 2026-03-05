import axiosClient from "./axiosClient";
import type { ModelInfo, TrainModelPayload } from "../types/model";

export async function listModels(): Promise<ModelInfo[]> {
  const response = await axiosClient.get<ModelInfo[]>("/models/");
  return response.data;
}

export async function trainModel(payload: TrainModelPayload): Promise<ModelInfo> {
  const response = await axiosClient.post<ModelInfo>("/models/train", payload);
  return response.data;
}

export async function deleteModel(modelId: string): Promise<void> {
  await axiosClient.delete(`/models/${modelId}`);
}
