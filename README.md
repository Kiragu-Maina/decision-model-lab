# Decision Model Lab

Decision Model Lab is an open benchmark and interactive demonstration for
local probabilistic decision models. Its `jevbench` harness accepts shared state
plus typed questions and scores probability distributions over caller-defined
answers. It is designed to compare Jev-compatible servers, SemIf-style direct
logit scorers, kev, and future local decision models without changing the test
corpus or scoring code.

The suite currently contains 86 cases and more than 200 decisions across nine
slices. It measures hard and soft accuracy, Brier score, log loss, calibration,
ordinal error, selective accuracy, perturbation stability, latency, throughput,
schema errors, and missing responses.

This is an independent research project inspired by the interface introduced
with TypeSafe AI's Jev announcement. It does not contain Jev, reproduce
TypeSafe's private evaluation, or report a score for Jev. The measured model
results in this repository are for the open Kev and SemIf implementations.

## What is included

- `src/jevbench/`: corpus generation, adapters, validation, metrics, and reports.
- `corpus/`: the benchmark definition and extension guidance.
- `web/`: the Next.js AI Bouncer demonstration, including replay mode.
- `tests/` and `web/tests/`: Python and TypeScript regression suites.
- `scripts/`: reproducibility, model startup, smoke-test, and verification tools.
- `docs/`: protocol, methodology, backend, and implementation documentation.

Model weights, upstream checkouts, virtual environments, generated reports,
and local caches are intentionally excluded from Git.

## AI Bouncer demo

`web/` is a working Next.js demonstration of the models as a decision layer in
front of risky software actions. It never executes the represented action. The
9:16 “Risk Depth Dive” makes five structured decisions visible, then a separate
conservative resolver returns `ALLOW`, `ASK A HUMAN`, or `BLOCK`.

Replay mode is deterministic synthetic data and works completely offline:

```bash
npm --prefix web install
npm --prefix web run dev
```

Open <http://127.0.0.1:3000>, leave the source on `REPLAY`, choose one of the
four traps, and select **Inspect action**. Every result-bearing screen retains
the `REPLAY` label.

For live local inference, run the web app natively on the Mac. The **Model
services** panel can start either host-native server and follows its real
OFFLINE → STARTING → RUNNING state. Startup logs are written under
`.models/logs/`. A model started from the panel gets a matching **Stop** control;
servers started elsewhere are labeled **External** and are never killed by the
app. You can also start them in separate terminals:

```bash
scripts/start_kev.sh      # http://127.0.0.1:8009
scripts/start_semif.sh    # http://127.0.0.1:8011
npm --prefix web run dev
```

Then choose `KEV`, `SEMIF`, or `BOTH LIVE`. Override endpoints with
`KEV_BASE_URL`, `SEMIF_BASE_URL`, and the deadline with `MODEL_TIMEOUT_MS`.
Unavailable servers produce a visible no-verdict state; they do not silently
allow an action.

Ollama is not required. These models already expose the typed `/v1/systemone`
contract through their native launchers, which preserves MLX/MPS acceleration
on this Mac.

### Docker-isolated demo

The production web image is isolated while model inference remains on the Mac:

```bash
docker compose --profile demo build demo
docker compose --profile demo up demo
```

The container reaches Kev and SemIf through `host.docker.internal`. Replay mode
still works when neither server is running. A container can report host model
status but deliberately cannot launch a macOS host process, so its start buttons
show **HOST ONLY**; start the models natively before using the Docker UI. The
evaluator remains a separate Docker service so a UI run and a benchmark run
cannot blur into one another.

### Recording workflow

1. Use Replay for a repeatable take, or start the selected live server first.
2. Open the page at 430×932 or crop the left 9:16 stage from desktop.
3. Choose a trap, press **Inspect action**, and expand **Review evidence**.
4. Keep the source badge and “Action not executed” line visible in the clip.

The shown 86.1% SemIf and 65.8% Kev figures are aggregate accuracy on this
repository’s fixed 202-decision benchmark. The percentages inside the dive are
per-request model probabilities—not accuracy and not production guarantees.

## Why the evaluator uses Docker but the models do not

On Apple Silicon, ordinary Docker Desktop Linux containers cannot use the
Mac's Metal/MPS acceleration. The intended topology is therefore:

```text
macOS host                           Docker Desktop VM
┌─────────────────────────────┐     ┌────────────────────────────┐
│ SemIf + MLX or kev + MPS    │     │ jevbench evaluator         │
│ localhost:8011 or :8009     │◀────│ host.docker.internal       │
│ Apple GPU accelerated       │     │ corpus, metrics, reports   │
└─────────────────────────────┘     └────────────────────────────┘
```

This keeps dependencies and scoring isolated while leaving inference on the
hardware-accelerated host. On an NVIDIA Linux machine, both layers can be
containerized later without changing the protocol.

## Local setup

The core suite has no runtime dependencies outside Python 3.11+.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
jevbench validate
```

Inspect exactly what will be sent before contacting a model:

```bash
jevbench dry-run --model local --output reports/requests.jsonl
```

Run against a TypeSafe-compatible local endpoint:

```bash
jevbench run \
  --backend http \
  --base-url http://127.0.0.1:8008 \
  --model kev-latest \
  --repetitions 3 \
  --output reports/kev.json
```

## Installed Apple-Silicon model servers

The ignored `.models` and `.venvs` directories keep upstream source, model
weights, package caches, and separate runtimes out of the benchmark package.
After cloning SemIf and kev as described in `docs/BACKENDS.md`, start exactly
one native server at a time:

```bash
scripts/start_semif.sh                       # SemIf Qwen3.5-4B, MLX, source precision
scripts/start_kev.sh                         # kev-0.5b, MPS, fp32
```

Both expose `POST /v1/systemone`. SemIf runs on port 8011 and kev on 8009.
The first launch downloads weights into `.models/cache`; later launches reuse
them. The SemIf bridge loads once and evaluates sibling questions as one
shared-state batch.

Compare reports only when their corpus digests match:

```bash
jevbench compare reports/kev.json reports/semif.json \
  --output reports/comparison.md
```

## Docker workflow

Start the model server natively on macOS first. Then validate the isolated
evaluator image:

```bash
docker compose build evaluator
docker compose run --rm evaluator validate
```

Run it against the host-native server:

```bash
docker compose run --rm evaluator run \
  --backend http \
  --base-url http://host.docker.internal:8009 \
  --model kev-0.5b \
  --repetitions 3 \
  --output reports/kev-0.5b.json
```

The `reports` directory is mounted read/write. The optional `replays` directory
is read-only so previously captured responses can be rescored without loading a
model.

## Fast development checks

```bash
PYTHONPATH=src python3 scripts/verify_corpus.py
PYTHONPATH=src python3 scripts/run_tests.py
PYTHONPATH=src python3 scripts/smoke_benchmark.py
```

## Corpus slices

- `routing`: support ownership, refund intent, and urgency.
- `evidence`: entailment, contradiction, and insufficient evidence.
- `safety`: allow/confirm/block decisions and impact.
- `policy`: explicit rule application.
- `sentiment`: categorical and ordinal judgments.
- `abstention`: catch-all behavior when no supplied specialist label fits.
- `adversarial`: instructions embedded in untrusted state.
- `long_context`: fact retrieval amid irrelevant material.
- `ambiguity`: soft target distributions for genuinely uncertain cases.

Each perturbation variant retains its base case's group identifier. That lets
the scorer directly measure option-order, question-order, paraphrase, and
irrelevant-context stability.

See [protocol](docs/PROTOCOL.md), [methodology](docs/METHODOLOGY.md), and
[backend integration](docs/BACKENDS.md) for the exact contracts and caveats.
