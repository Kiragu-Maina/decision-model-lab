import {
  evaluationRequestSchema,
  type EvaluationResponse,
  type ModelFailure,
  type ModelId,
  type ModelResult,
} from "@/lib/contracts";
import { resolveVerdict } from "@/lib/decision";
import { callModel } from "@/lib/model-adapter";
import { scenarioById } from "@/lib/scenarios";

export const runtime = "nodejs";

const requestedModels = (
  source: "replay" | "kev" | "semif" | "both",
): ModelId[] =>
  source === "kev"
    ? ["kev"]
    : source === "semif"
      ? ["semif"]
      : ["kev", "semif"];

export async function POST(request: Request): Promise<Response> {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return Response.json(
      { error: "Request body must be valid JSON." },
      { status: 400 },
    );
  }

  const parsed = evaluationRequestSchema.safeParse(body);
  if (!parsed.success) {
    return Response.json(
      {
        error: "Request validation failed.",
        issues: parsed.error.flatten().fieldErrors,
      },
      { status: 422 },
    );
  }

  const input = parsed.data;
  const models = requestedModels(input.source);
  if (input.source === "replay") {
    const scenario = scenarioById(input.scenarioId);
    if (!scenario)
      return Response.json(
        { error: "Replay scenario not found." },
        { status: 404 },
      );
    const results = models.map((model) => scenario.replay[model]);
    const response: EvaluationResponse = {
      requestId: crypto.randomUUID(),
      source: input.source,
      replay: true,
      results,
      failures: [],
      resolution: resolveVerdict(results, [], models),
      safeSimulation: true,
    };
    return Response.json(response);
  }

  const settled = await Promise.all(
    models.map((model) => callModel(input, model)),
  );
  const results = settled.filter(
    (item): item is ModelResult => "dimensions" in item,
  );
  const failures = settled.filter(
    (item): item is ModelFailure => !("dimensions" in item),
  );
  const response: EvaluationResponse = {
    requestId: crypto.randomUUID(),
    source: input.source,
    replay: false,
    results,
    failures,
    resolution: resolveVerdict(results, failures, models),
    safeSimulation: true,
  };
  return Response.json(response, { status: results.length ? 200 : 503 });
}
