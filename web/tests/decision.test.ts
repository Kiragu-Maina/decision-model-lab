import assert from "node:assert/strict";
import test from "node:test";

import type { ModelFailure, ModelResult } from "../lib/contracts";
import { deriveModelBand, resolveVerdict } from "../lib/decision";
import { scenarios } from "../lib/scenarios";

const fixture = scenarios[0].replay;

test("injection and critical risk fail closed", () => {
  assert.equal(deriveModelBand(fixture.kev), "block");
  assert.equal(resolveVerdict([fixture.kev], [], ["kev"]).verdict, "block");
});

test("a forbidden authorization is a hard block", () => {
  const result: ModelResult = structuredClone(fixture.kev);
  result.dimensions.injection = {
    selection: "false",
    probability: 0.99,
    probabilities: { false: 0.99, true: 0.01 },
  };
  result.dimensions.risk = {
    selection: "low",
    probability: 0.95,
    probabilities: { low: 0.95, guarded: 0.03, high: 0.01, critical: 0.01 },
  };
  result.dimensions.authorization = {
    selection: "forbidden",
    probability: 0.8,
    probabilities: { allowed: 0.2, forbidden: 0.8 },
  };
  assert.equal(deriveModelBand(result), "block");
});

test("an irreversible action requires confirmation", () => {
  const result: ModelResult = structuredClone(fixture.kev);
  result.dimensions.authorization = {
    selection: "allowed",
    probability: 0.98,
    probabilities: { allowed: 0.98, forbidden: 0.02 },
  };
  result.dimensions.sensitivity = {
    selection: "internal",
    probability: 0.95,
    probabilities: { internal: 0.95, restricted: 0.05 },
  };
  result.dimensions.injection = {
    selection: "false",
    probability: 0.99,
    probabilities: { false: 0.99, true: 0.01 },
  };
  result.dimensions.risk = {
    selection: "low",
    probability: 0.9,
    probabilities: { low: 0.9, guarded: 0.08, high: 0.01, critical: 0.01 },
  };
  result.dimensions.reversibility = {
    selection: "irreversible",
    probability: 0.8,
    probabilities: { reversible: 0.2, irreversible: 0.8 },
  };
  result.band = deriveModelBand(result);
  assert.equal(result.band, "confirm");
});

test("disagreement and partial model failure require a human", () => {
  const allow: ModelResult = structuredClone(fixture.kev);
  for (const [key, decision] of Object.entries(allow.dimensions)) {
    if (key === "authorization")
      Object.assign(decision, { selection: "allowed" });
    if (key === "sensitivity")
      Object.assign(decision, { selection: "internal" });
    if (key === "reversibility")
      Object.assign(decision, { selection: "reversible" });
    if (key === "injection")
      Object.assign(decision, {
        selection: "false",
        probabilities: { false: 0.99, true: 0.01 },
      });
    if (key === "risk") Object.assign(decision, { selection: "low" });
  }
  allow.band = deriveModelBand(allow);
  const confirm: ModelResult = structuredClone(allow);
  confirm.model = "semif";
  confirm.dimensions.reversibility.selection = "irreversible";
  confirm.band = deriveModelBand(confirm);
  assert.equal(
    resolveVerdict([allow, confirm], [], ["kev", "semif"]).verdict,
    "confirm",
  );

  const failure: ModelFailure = {
    model: "semif",
    code: "unavailable",
    message: "offline",
  };
  assert.equal(
    resolveVerdict([allow], [failure], ["kev", "semif"]).verdict,
    "confirm",
  );
});

test("no valid results never produce an allow verdict", () => {
  assert.equal(resolveVerdict([], [], ["kev"]).verdict, "unavailable");
});
