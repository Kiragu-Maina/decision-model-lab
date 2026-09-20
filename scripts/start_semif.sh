#!/bin/sh
set -eu

project_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
exec env \
  HF_HOME="$project_root/.models/cache/semif" \
  HF_HUB_DISABLE_XET=1 \
  PYTHONPATH="$project_root/.models/repos/semif/src" \
  "$project_root/.venvs/semif/bin/python" "$project_root/adapters/semif_server.py" "$@"
