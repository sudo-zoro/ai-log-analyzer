import axios from "axios";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  createContext,
  type ReactNode,
  useContext,
  useEffect,
  useState,
} from "react";
import { trainModel } from "../api/modelApi";
import { generateInsights } from "../api/insightsApi";
import type { DetectionRun } from "../types/detection";
import type { ExplainPayload, ExplainResponse } from "../types/insights";
import type { ModelInfo, TrainModelPayload } from "../types/model";

type AnalysisSessionContextValue = {
  selectedDetection: DetectionRun | null;
  setSelectedDetection: (detection: DetectionRun | null) => void;
  insights: ExplainResponse | null;
  isGeneratingInsights: boolean;
  insightsError: string;
  generateDetectionInsights: (payload: ExplainPayload) => void;
  clearInsights: () => void;
  activeTrainingRequest: TrainModelPayload | null;
  latestTrainedModel: ModelInfo | null;
  isTrainingModel: boolean;
  trainingModelError: string;
  startModelTraining: (payload: TrainModelPayload) => void;
  clearModelTraining: () => void;
};

const SELECTED_DETECTION_STORAGE_KEY = "secrag.selectedDetection";
const INSIGHTS_STORAGE_KEY = "secrag.insights";
const ACTIVE_TRAINING_REQUEST_STORAGE_KEY = "secrag.activeTrainingRequest";
const LATEST_TRAINED_MODEL_STORAGE_KEY = "secrag.latestTrainedModel";

const AnalysisSessionContext = createContext<AnalysisSessionContextValue | null>(null);

function readSessionStorage<T>(key: string): T | null {
  if (typeof window === "undefined") {
    return null;
  }

  const value = window.sessionStorage.getItem(key);
  if (!value) {
    return null;
  }

  try {
    return JSON.parse(value) as T;
  } catch {
    return null;
  }
}

type AnalysisSessionProviderProps = {
  children: ReactNode;
};

export function AnalysisSessionProvider({ children }: AnalysisSessionProviderProps) {
  const queryClient = useQueryClient();
  const [selectedDetection, setSelectedDetectionState] = useState<DetectionRun | null>(() =>
    readSessionStorage<DetectionRun>(SELECTED_DETECTION_STORAGE_KEY),
  );
  const [insights, setInsights] = useState<ExplainResponse | null>(() =>
    readSessionStorage<ExplainResponse>(INSIGHTS_STORAGE_KEY),
  );
  const [activeTrainingRequest, setActiveTrainingRequest] = useState<TrainModelPayload | null>(() =>
    readSessionStorage<TrainModelPayload>(ACTIVE_TRAINING_REQUEST_STORAGE_KEY),
  );
  const [latestTrainedModel, setLatestTrainedModel] = useState<ModelInfo | null>(() =>
    readSessionStorage<ModelInfo>(LATEST_TRAINED_MODEL_STORAGE_KEY),
  );

  const insightsMutation = useMutation({
    mutationFn: (payload: ExplainPayload) => generateInsights(payload),
    onSuccess: (response) => {
      setInsights(response);
    },
  });
  const trainingMutation = useMutation({
    mutationFn: (payload: TrainModelPayload) => trainModel(payload),
    onMutate: (payload) => {
      setActiveTrainingRequest(payload);
    },
    onSuccess: async (response) => {
      setLatestTrainedModel(response);
      await queryClient.invalidateQueries({ queryKey: ["models"] });
    },
  });

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    if (selectedDetection) {
      window.sessionStorage.setItem(SELECTED_DETECTION_STORAGE_KEY, JSON.stringify(selectedDetection));
    } else {
      window.sessionStorage.removeItem(SELECTED_DETECTION_STORAGE_KEY);
    }
  }, [selectedDetection]);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    if (insights) {
      window.sessionStorage.setItem(INSIGHTS_STORAGE_KEY, JSON.stringify(insights));
    } else {
      window.sessionStorage.removeItem(INSIGHTS_STORAGE_KEY);
    }
  }, [insights]);
  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    if (activeTrainingRequest) {
      window.sessionStorage.setItem(ACTIVE_TRAINING_REQUEST_STORAGE_KEY, JSON.stringify(activeTrainingRequest));
    } else {
      window.sessionStorage.removeItem(ACTIVE_TRAINING_REQUEST_STORAGE_KEY);
    }
  }, [activeTrainingRequest]);
  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    if (latestTrainedModel) {
      window.sessionStorage.setItem(LATEST_TRAINED_MODEL_STORAGE_KEY, JSON.stringify(latestTrainedModel));
    } else {
      window.sessionStorage.removeItem(LATEST_TRAINED_MODEL_STORAGE_KEY);
    }
  }, [latestTrainedModel]);

  const setSelectedDetection = (detection: DetectionRun | null) => {
    setSelectedDetectionState(detection);
    setInsights(null);
    insightsMutation.reset();
  };

  const generateDetectionInsights = (payload: ExplainPayload) => {
    insightsMutation.mutate(payload);
  };

  let insightsError = "";
  if (insightsMutation.error) {
    if (axios.isAxiosError(insightsMutation.error)) {
      insightsError =
        (insightsMutation.error.response?.data as { detail?: string } | undefined)?.detail ??
        insightsMutation.error.message;
    } else {
      insightsError = "Failed to generate insights.";
    }
  }

  const clearInsights = () => {
    setInsights(null);
    insightsMutation.reset();
  };
  const startModelTraining = (payload: TrainModelPayload) => {
    setLatestTrainedModel(null);
    trainingMutation.reset();
    trainingMutation.mutate(payload);
  };

  let trainingModelError = "";
  if (trainingMutation.error) {
    if (axios.isAxiosError(trainingMutation.error)) {
      trainingModelError =
        (trainingMutation.error.response?.data as { detail?: string } | undefined)?.detail ??
        trainingMutation.error.message;
    } else {
      trainingModelError = "Training failed.";
    }
  }

  const clearModelTraining = () => {
    setActiveTrainingRequest(null);
    setLatestTrainedModel(null);
    trainingMutation.reset();
  };

  return (
    <AnalysisSessionContext.Provider
      value={{
        selectedDetection,
        setSelectedDetection,
        insights,
        isGeneratingInsights: insightsMutation.isPending,
        insightsError,
        generateDetectionInsights,
        clearInsights,
        activeTrainingRequest,
        latestTrainedModel,
        isTrainingModel: trainingMutation.isPending,
        trainingModelError,
        startModelTraining,
        clearModelTraining,
      }}
    >
      {children}
    </AnalysisSessionContext.Provider>
  );
}

export function useAnalysisSession() {
  const context = useContext(AnalysisSessionContext);
  if (!context) {
    throw new Error("useAnalysisSession must be used within AnalysisSessionProvider.");
  }
  return context;
}
