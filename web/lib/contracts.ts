import { z } from "zod";

export const dimensionKeys = [
  "authorization",
  "sensitivity",
  "reversibility",
  "injection",
  "risk",
] as const;

export type DimensionKey = (typeof dimensionKeys)[number];
export type SourceMode = "replay" | "kev" | "semif" | "both";
export type ModelId = "kev" | "semif";
export type ModelServiceState =
  | "running"
  | "offline"
  | "starting"
  | "stopping"
  | "error";
export type Verdict = "allow" | "confirm" | "block" | "unavailable";
export type ModelBand = Exclude<Verdict, "unavailable">;

export const evaluationRequestSchema = z.object({
  scenarioId: z.string().min(1).max(64),
  source: z.enum(["replay", "kev", "semif", "both"]),
  action: z.string().trim().min(3).max(500),
  context: z.string().trim().min(3).max(2_000),
  policy: z.string().trim().min(3).max(1_000),
});

export type EvaluationRequest = z.infer<typeof evaluationRequestSchema>;

export interface DimensionDecision {
  selection: string;
  probability: number;
  probabilities: Record<string, number>;
}

export interface ModelResult {
  model: ModelId;
  modelLabel: string;
  mode: "replay" | "live";
  latencyMs: number;
  dimensions: Record<DimensionKey, DimensionDecision>;
  confidence: number;
  band: ModelBand;
}

export interface ModelFailure {
  model: ModelId;
  code: "unavailable" | "timeout" | "invalid_response";
  message: string;
}

export interface ModelServiceStatus {
  model: ModelId;
  label: string;
  endpoint: string;
  state: ModelServiceState;
  launchable: boolean;
  stoppable: boolean;
  message: string;
}

export interface Resolution {
  verdict: Verdict;
  reason: string;
  disagreement: boolean;
  requestedModels: ModelId[];
}

export interface EvaluationResponse {
  requestId: string;
  source: SourceMode;
  replay: boolean;
  results: ModelResult[];
  failures: ModelFailure[];
  resolution: Resolution;
  safeSimulation: true;
}
