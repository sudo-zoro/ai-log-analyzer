import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { deleteModel, listModels, trainModel } from "../api/modelApi";
import type { TrainModelPayload } from "../types/model";

const MODELS_QUERY_KEY = ["models"];

export function useModels() {
  return useQuery({
    queryKey: MODELS_QUERY_KEY,
    queryFn: listModels,
  });
}

export function useTrainModel() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: TrainModelPayload) => trainModel(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: MODELS_QUERY_KEY });
    },
  });
}

export function useDeleteModel() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (modelId: string) => deleteModel(modelId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: MODELS_QUERY_KEY });
    },
  });
}
