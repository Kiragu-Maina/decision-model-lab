import type {
  DimensionDecision,
  ModelBand,
  ModelFailure,
  ModelId,
  ModelResult,
  Resolution,
} from "./contracts";

const unsafeSelections = new Set([
  "forbidden",
  "restricted",
  "true",
  "critical",
]);
const guardedSelections = new Set([
  "needs_approval",
  "confidential",
  "partially_reversible",
  "irreversible",
  "guarded",
  "high",
]);

function unsafe(decision: DimensionDecision): boolean {
  return unsafeSelections.has(decision.selection);
}

export function deriveModelBand(
  result: Pick<ModelResult, "dimensions">,
): ModelBand {
  const dimensions = result.dimensions;

  if (
    unsafe(dimensions.authorization) ||
    unsafe(dimensions.sensitivity) ||
    unsafe(dimensions.injection) ||
    (dimensions.injection.probabilities.true ?? 0) >= 0.7 ||
    dimensions.risk.selection === "critical"
  ) {
    return "block";
  }

  if (
    Object.values(dimensions).some((decision) =>
      guardedSelections.has(decision.selection),
    )
  ) {
    return "confirm";
  }

  return "allow";
}

export function resolveVerdict(
  results: ModelResult[],
  failures: ModelFailure[],
  requestedModels: ModelId[],
): Resolution {
  if (results.length === 0) {
    return {
      verdict: "unavailable",
      reason: "No selected model returned a valid decision.",
      disagreement: false,
      requestedModels,
    };
  }

  if (results.some((result) => result.band === "block")) {
    return {
      verdict: "block",
      reason: "A model found a hard safety boundary in the request.",
      disagreement: new Set(results.map((result) => result.band)).size > 1,
      requestedModels,
    };
  }

  const disagreement = new Set(results.map((result) => result.band)).size > 1;
  if (
    failures.length > 0 ||
    disagreement ||
    results.some((result) => result.band === "confirm")
  ) {
    return {
      verdict: "confirm",
      reason: failures.length
        ? "Only part of the requested evaluation completed. Ask a human."
        : disagreement
          ? "The models disagree. Ask a human before acting."
          : "The action needs explicit human approval.",
      disagreement,
      requestedModels,
    };
  }

  return {
    verdict: "allow",
    reason: "Every selected model cleared the policy checks.",
    disagreement: false,
    requestedModels,
  };
}

export function averageConfidence(
  dimensions: ModelResult["dimensions"],
): number {
  const probabilities = Object.values(dimensions).map(
    (decision) => decision.probability,
  );
  return (
    probabilities.reduce((sum, value) => sum + value, 0) / probabilities.length
  );
}
