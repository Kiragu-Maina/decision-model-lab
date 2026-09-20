# Backend integration

## HTTP backend

Use this for kev or any server implementing `POST /v1/systemone`:

```bash
jevbench run --backend http --base-url http://127.0.0.1:8008 --model kev-latest
```

`--base-url` may include `/v1/systemone`; the client will not append it twice.
Set `JEVBENCH_API_KEY` or pass `--api-key` when authentication is enabled.

Inside Docker Desktop on macOS, use the host gateway:

```bash
jevbench run --backend http \
  --base-url http://host.docker.internal:8008 \
  --model kev-latest
```

## Command backend

Use this when a project has a Python/MLX inference API but no HTTP service. A
SemIf adapter can import its scorer, read the standard request from stdin, and
write the normalized response to stdout. The harness adds `case_id` but sends
no gold label.

```bash
jevbench run --backend command \
  --command "python adapters/semif_adapter.py" \
  --model qwen3.5-4b
```

The command backend is deliberately sequential. For realistic throughput,
prefer a persistent HTTP adapter so model loading and process startup are not
included in every case.

## Native Apple-Silicon setup

The evaluator belongs in Docker, but MLX/MPS inference must remain on macOS to
reach Metal. The tested setup uses Python 3.12 and separate environments:

```bash
mkdir -p .models/repos .models/cache .venvs
git clone --depth 1 https://github.com/TheoLeeCJ/SemIf.git .models/repos/semif
git clone --depth 1 https://github.com/jaredpalmer/kev.git .models/repos/kev
UV_CACHE_DIR=.models/uv-cache uv venv .venvs/semif --python /opt/homebrew/bin/python3.12
UV_CACHE_DIR=.models/uv-cache uv pip install --python .venvs/semif/bin/python -e '.models/repos/semif[test,mlx]'
UV_CACHE_DIR=.models/uv-cache uv venv .venvs/kev --python /opt/homebrew/bin/python3.12
UV_CACHE_DIR=.models/uv-cache uv pip install --python .venvs/kev/bin/python -r adapters/kev-requirements.txt
```

The separate kev requirements file works around upstream editable-package
discovery treating its research directories as packages. Its source is loaded
directly with `PYTHONPATH`; no code in the clone is modified.

Start one server, probe it, run the containerized evaluator, then stop it before
loading the other model:

```bash
scripts/start_semif.sh
PYTHONPATH=src python3 scripts/probe_backend.py --base-url http://127.0.0.1:8011 --expect-model semif-qwen3.5-4b-mlx

scripts/start_kev.sh
PYTHONPATH=src python3 scripts/probe_backend.py --base-url http://127.0.0.1:8009 --expect-model kev-0.5b
```

## Replay backend

Use replay to debug metrics and regenerate reports without inference:

```bash
jevbench run --backend replay --replay replays/kev.jsonl --model kev-replay
```

Keep raw provider responses in the replay file. This preserves enough evidence
to re-run validation after the scorer changes.

## Oracle backend

The oracle copies the corpus target distributions. It exists only to exercise
the runner, metrics, perturbation pairing, and report generation:

```bash
jevbench run --backend oracle --model oracle --output reports/oracle.json
```

Oracle results are harness tests, not a model baseline, and must never appear
in a performance comparison as if they came from inference.

## Local adapters

- **kev:** use its existing TypeSafe-compatible server directly.
- **SemIf:** `adapters/semif_server.py` wraps its persistent MLX scorer, preserves
  runtime-defined option descriptions, batches questions sharing a state, and
  returns complete distributions rather than only the winning token.
- **Laya/Decider:** use their native server when Apple-Silicon execution is
  verified; do not route through Ollama because their custom decision heads
  are part of the model.
