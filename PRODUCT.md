# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Next.js was explicitly requested by the user. The app uses the App Router, TypeScript, and a server route that can reach host-native model servers. Docker remains the isolation boundary for the existing benchmark evaluator rather than the default inference runtime on Apple Silicon.

## Users

The primary user is a technical creator recording a short, visually legible TikTok demonstration of small local decision models. Their job is to turn an abstract classifier into an application viewers understand in seconds, while retaining enough evidence for a technically literate audience to inspect the result.

Secondary users are developers evaluating whether Kev, SemIf, or both can sit in front of an AI agent as a typed decision layer.

## Product Purpose

AI Bouncer simulates an authorization checkpoint in front of high-impact software actions. A scenario supplies the proposed action, the evidence available to the agent, and a policy. Kev and/or SemIf classify the decision into structured signals, and the interface resolves those signals into `ALLOW`, `ASK A HUMAN`, or `BLOCK`.

Success means a viewer can understand the action, the hidden trap, the models' disagreement, the probability/confidence information, and the final safety disposition in one short recording.

## Positioning

The application does not ask a general chat model to write another paragraph. It makes small local models expose a compact, inspectable decision contract that ordinary software can branch on. A conservative resolver turns model outputs into an explicit control point before an action would execute.

## Operating Context

- The creator chooses a prepared scenario or edits one.
- The app can replay deterministic, clearly labeled fixtures with no model process running.
- Live mode calls host-native Kev and SemIf HTTP adapters already included in this repository.
- The demonstration never executes the represented refund, deletion, message, or price change.
- The existing Docker benchmark remains available to verify the models independently of the demo UI.

## Capabilities and Constraints

- Required decisions: authorization, sensitivity, reversibility, injection risk, and overall risk.
- Required outcomes: `ALLOW`, `ASK A HUMAN`, and `BLOCK`.
- Both live models may be selected together, and disagreement must remain visible.
- Backend unavailability and malformed responses must fail visibly and must not be presented as a safe decision.
- Replay data must be labeled as replay/synthetic, never as a fresh model run.
- Model accuracy is evidence from this repository's fixed benchmark, not a guarantee for arbitrary production traffic.
- Inference is local-first. No cloud model or Ollama dependency is required.
- Actual side effects are out of scope.

## Evidence on Hand

- `reports/comparison.json` records SemIf at 86.1% aggregate accuracy and Kev at 65.8% across 202 decisions in the versioned local benchmark.
- The same report records mean request latency of about 1,366 ms for SemIf and 78 ms for Kev on this Mac test setup.
- `reports/semif-qwen3.5-4b-mlx.json` and `reports/kev-0.5b.json` contain the detailed measurements.
- `corpus/` and `docs/METHODOLOGY.md` document the evaluation set and method.
- No customer claims, production reliability claims, testimonials, or deployment claims exist and none should be fabricated.

## Product Principles

1. Make the decision inspectable before making it impressive.
2. Label replay, live inference, benchmark evidence, and product policy as different things.
3. Fail closed when a live model is unavailable or returns an invalid contract.
4. Keep the first screen understandable in a vertical video without hiding technical depth.
5. Preserve the difference between confidence and measured accuracy.

## Accessibility & Inclusion

The core verdict must never rely on color alone. All controls require visible labels and keyboard focus, motion must respect reduced-motion preferences, and the interface should maintain WCAG AA contrast for primary text and interactive controls.
