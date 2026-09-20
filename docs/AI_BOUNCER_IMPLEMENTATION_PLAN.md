# AI Bouncer implementation plan

Status: approved for implementation from the user's request to build the proposed Next.js demonstration.

## 1. Outcome

Build a local-first Next.js application that demonstrates Kev and SemIf as a software decision layer. A viewer sees an AI agent propose a risky action, watches each model classify the important properties, and then sees a conservative policy resolver return `ALLOW`, `ASK A HUMAN`, or `BLOCK`.

The deliverable is a working vertical-first demo, not a slide deck or a fake chat transcript. It supports deterministic replay for recording and optional live inference through the repository's existing model adapters.

## 2. Audience and primary story

The first audience is a TikTok viewer who has never heard of a “decision model.” The story must read in under ten seconds:

1. An AI agent wants to perform an action.
2. A hidden fact makes that action dangerous or ambiguous.
3. Kev and SemIf inspect the action as structured decisions.
4. Their probabilities and any disagreement are visible.
5. The policy stops, escalates, or allows the action.

The second audience is a developer who can open the technical drawer and inspect the exact request, model outputs, aggregation rule, latency, and benchmark context.

## 3. Scope

### In scope

- Next.js App Router application in `web/`.
- A 9:16 recording surface that also expands cleanly on desktop.
- Four prepared scenarios: refund prompt injection, production database deletion, confidential payroll attachment, and a zero-price commerce update.
- Editable action, context/evidence, and policy fields.
- Explicit source modes: Replay, Kev live, SemIf live, and Both live.
- Structured decision cards for authorization, sensitivity, reversibility, injection, and risk.
- A conservative final resolver and visible disagreement state.
- Local HTTP integration with the existing Kev and SemIf launchers.
- Input validation, timeouts, graceful unavailable states, tests, production build, runtime smoke test, responsive screenshots, and visual linting.

### Out of scope

- Executing any represented action.
- Authentication, persistent accounts, a production database, or remote deployment.
- Claims that benchmark accuracy transfers directly to production.
- Hiding replay data behind a “live” label.
- Requiring Ollama or putting Apple-Silicon inference inside Docker.

## 4. System design

```text
Browser
  │
  ├── Replay mode ── deterministic fixture engine
  │
  └── Live mode ─── POST /api/evaluate
                         │
                         ├── Kev adapter   http://127.0.0.1:8009/v1/systemone
                         └── SemIf adapter http://127.0.0.1:8011/v1/systemone
                                  │
                                  └── validated typed decisions

All successful paths ── conservative resolver ── ALLOW / ASK A HUMAN / BLOCK
```

The browser never calls a model process directly. The Next.js server route validates the request, applies deadlines, calls only the selected local endpoints, validates their responses, and returns a normalized envelope. The UI uses the same envelope for replay and live results.

### Decision contract

Each model result contains:

- source and model identity;
- whether the result is replay or live;
- latency;
- one selection and probability distribution for each categorical decision;
- a normalized risk score and confidence;
- an optional diagnostic error.

The app-level resolver is deterministic and separate from the models:

- `BLOCK` when any valid selected model reports injection, forbidden authorization, critical sensitivity, or critical risk;
- `ASK A HUMAN` when the evidence is ambiguous, a destructive action is not clearly reversible, the models disagree on the final band, or only part of a requested live evaluation succeeds;
- `ALLOW` only when every requested valid result clears the policy thresholds;
- no valid model result means no verdict and a visible unavailable state.

## 5. Interface structure

### First viewport

The recording surface opens on a single proposed action with a compact “agent request” header, a large decision aperture in the center, and a thumb-reachable run control. The outcome typography is large enough to survive TikTok compression. A small source badge always says `REPLAY` or `LIVE`.

### Interaction sequence

1. Pick a scenario from the scenario rail.
2. Tap “Inspect action.”
3. The request locks and the decision lanes resolve in a short, reduced-motion-safe sequence.
4. The final policy shutter lands on the verdict.
5. Expand “Why?” for model probabilities and “Evidence” for the hidden trap.
6. Switch to Both to expose agreement or disagreement.

### Desktop adaptation

Desktop keeps the vertical recording stage intact and places the editable scenario/policy console beside it. This lets a creator frame the 9:16 panel while changing inputs without the recording surface jumping.

## 6. Delivery phases

### Phase A — contracts and fixtures

- Define TypeScript request, response, decision, scenario, and resolver types.
- Encode four replay scenarios with deterministic outputs.
- Implement and unit-test input validation and conservative resolution.

### Phase B — model integration

- Implement the Next.js route and per-model adapters.
- Translate the product request into the existing `/v1/systemone` protocol.
- Normalize probabilities and reject malformed payloads.
- Add timeout and partial-failure behavior.

### Phase C — product surface

- Build the vertical decision stage, scenario rail, source selector, verdict state, probability inspection, and editable desktop console.
- Add meaningful empty, loading, unavailable, disagreement, and success states.
- Add share/record helpers without claiming to upload or execute anything.

### Phase D — validation and handoff

- Run formatting, lint, type checks, unit tests, production build, and runtime smoke tests.
- Capture desktop and 9:16 screenshots.
- Run the interface detector and fix high-severity findings.
- Verify keyboard use, reduced motion, and basic contrast.
- Document exact commands for replay, live models, Docker benchmark isolation, and screen recording.

## 7. Verification matrix

| Risk | Verification |
| --- | --- |
| Replay mistaken for live inference | Persistent source labels and UI/API contract tests |
| One model silently fails | Partial-failure test and visible per-model unavailable card |
| Unsafe action appears allowed | Resolver unit cases for injection, forbidden auth, irreversible actions, disagreement, and empty results |
| Probability confused with accuracy | Separate UI labels and explanatory copy; benchmark figure sourced from local reports |
| Vertical layout clips | Browser capture at 430×932 and visual inspection |
| Desktop recording surface loses shape | Browser capture at 1440×1000 |
| Live servers absent | Runtime smoke test expects a graceful non-200 model diagnostic, not an application crash |
| Existing benchmark regresses | Run the original Python unit suite after integration |

## 8. Acceptance criteria

- The app runs with `npm --prefix web run dev` and Replay mode works with no model process.
- A viewer can reach a legible final verdict in two interactions from page load.
- Both-live mode calls Kev and SemIf independently and shows disagreement or partial failure.
- The app never performs the represented action.
- Replay results are labeled on every result-bearing view.
- Confidence, probability, and benchmark accuracy are named separately.
- Malformed inputs and unavailable model servers have intentional visible states.
- Formatting, lint, types, tests, production build, runtime smoke, responsive captures, visual detector, documentation checks, and the existing benchmark tests all pass.

## 9. Run topology

- UI and server route: host-native Node/Next.js for fast iteration.
- Kev and SemIf: host-native Python/MLX, one server per port, because that is the tested Mac path.
- Benchmark evaluator: Docker Compose, because isolation and reproducibility matter more than direct Metal access there.
- Ollama: not required for this build.

This separation keeps the demonstration simple while preserving the already-tested isolation boundary for evaluation.
