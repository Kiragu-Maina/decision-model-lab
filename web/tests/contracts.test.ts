import assert from "node:assert/strict";
import test from "node:test";

import { evaluationRequestSchema } from "../lib/contracts";
import { callModel, normalizeModelResponse } from "../lib/model-adapter";
import { scenarios } from "../lib/scenarios";

test("every replay fixture contains both complete model results", () => {
  assert.equal(scenarios.length, 4);
  for (const scenario of scenarios) {
    assert.deepEqual(Object.keys(scenario.replay).sort(), ["kev", "semif"]);
    for (const result of Object.values(scenario.replay)) {
      assert.deepEqual(Object.keys(result.dimensions).sort(), [
        "authorization",
        "injection",
        "reversibility",
        "risk",
        "sensitivity",
      ]);
      assert.ok(result.confidence >= 0 && result.confidence <= 1);
    }
  }
});

test("malformed product requests are rejected", () => {
  const parsed = evaluationRequestSchema.safeParse({
    scenarioId: "x",
    source: "kev",
    action: "",
    context: "x",
  });
  assert.equal(parsed.success, false);
});

test("TypeSafe model responses normalize score and noul questions", () => {
  const probabilities = {
    authorization: {
      type: "choice",
      choice: "allowed",
      probabilities: { allowed: 0.9, forbidden: 0.1 },
    },
    sensitivity: {
      type: "choice",
      choice: "internal",
      probabilities: { internal: 0.9, restricted: 0.1 },
    },
    reversibility: {
      type: "choice",
      choice: "reversible",
      probabilities: { reversible: 0.8, irreversible: 0.2 },
    },
    injection: { type: "noul", noul: 0.12 },
    risk: {
      type: "score",
      probabilities: { "0": 0.7, "1": 0.2, "2": 0.08, "3": 0.02 },
    },
  };
  const result = normalizeModelResponse(
    { model: "kev-test", answers: probabilities },
    "kev",
    5,
  );
  assert.equal(result.dimensions.injection.selection, "false");
  assert.equal(result.dimensions.risk.selection, "low");
  assert.equal(result.band, "allow");
});

test("unavailable live backends return a diagnostic instead of throwing", async () => {
  const input = {
    scenarioId: scenarios[0].id,
    source: "kev" as const,
    action: scenarios[0].action,
    context: scenarios[0].context,
    policy: scenarios[0].policy,
  };
  const failedFetch = (() =>
    Promise.reject(new TypeError("connection refused"))) as typeof fetch;
  const result = await callModel(input, "kev", failedFetch);
  assert.ok("code" in result);
  assert.equal("code" in result && result.code, "unavailable");
});
