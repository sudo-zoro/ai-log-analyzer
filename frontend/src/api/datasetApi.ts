import axiosClient from "./axiosClient";
import type { Dataset, UploadDatasetPayload } from "../types/dataset";

export async function listDatasets(): Promise<Dataset[]> {
  const response = await axiosClient.get<Dataset[]>("/datasets/");
  return response.data;
}

export async function uploadDataset(payload: UploadDatasetPayload): Promise<Dataset> {
  const formData = new FormData();
  formData.append("name", payload.name);
  formData.append("file", payload.file);

  const response = await axiosClient.post<Dataset>("/datasets/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}

export async function deleteDataset(datasetId: string): Promise<void> {
  await axiosClient.delete(`/datasets/${datasetId}`);
}
