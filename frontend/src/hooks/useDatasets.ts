import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { deleteDataset, listDatasets, uploadDataset } from "../api/datasetApi";
import type { UploadDatasetPayload } from "../types/dataset";

const DATASETS_QUERY_KEY = ["datasets"];

export function useDatasets() {
  return useQuery({
    queryKey: DATASETS_QUERY_KEY,
    queryFn: listDatasets,
  });
}

export function useUploadDataset() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: UploadDatasetPayload) => uploadDataset(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: DATASETS_QUERY_KEY });
    },
  });
}

export function useDeleteDataset() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (datasetId: string) => deleteDataset(datasetId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: DATASETS_QUERY_KEY });
    },
  });
}
