#!/bin/sh
set -eu

project_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
exec env \
  HF_HOME="$project_root/.models/cache/kev" \
  KEV_DTYPE=fp32 \
  PYTHONPATH="$project_root/.models/repos/kev" \
  "$project_root/.venvs/kev/bin/python" -m kev.serve \
  --run jaredpalmer/kev-0.5b --port 8009 "$@"
