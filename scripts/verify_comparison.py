#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("comparison", type=Path)
    parser.add_argument("semif_report", type=Path)
    parser.add_argument("kev_report", type=Path)
    args = parser.parse_args()
    comparison = json.loads(args.comparison.read_text(encoding="utf-8"))
    reports = [json.loads(path.read_text(encoding="utf-8")) for path in (args.semif_report, args.kev_report)]
    expected_names = ["semif-qwen3.5-4b-mlx", "kev-0.5b"]
    actual_names = [entry.get("model") for entry in comparison.get("models", [])]
    digests = {report["corpus"]["digest"] for report in reports}
    if len(digests) != 1 or comparison.get("corpus_digest") != next(iter(digests)):
        raise SystemExit("comparison corpus digest mismatch")
    if actual_names != expected_names:
        raise SystemExit(f"comparison model order mismatch: {actual_names}")
    for entry, report in zip(comparison["models"], reports, strict=True):
        if entry.get("summary") != report["metrics"]["summary"]:
            raise SystemExit(f"comparison metrics mismatch for {entry.get('model')}")
        if entry.get("coverage", {}).get("error_count") != 0:
            raise SystemExit(f"comparison contains errors for {entry.get('model')}")
    print("comparison verified: semif-qwen3.5-4b-mlx vs kev-0.5b")


if __name__ == "__main__":
    main()
