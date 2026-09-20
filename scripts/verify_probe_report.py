#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    parser.add_argument("--expect-model", required=True)
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    coverage = report.get("metrics", {}).get("coverage", {})
    predictions = report.get("predictions", [])
    checks = {
        "model": report.get("run", {}).get("model") == args.expect_model,
        "HTTP backend": report.get("run", {}).get("backend") == "http",
        "one requested case": coverage.get("requested_cases") == 1,
        "one valid case": coverage.get("valid_cases") == 1,
        "zero errors": coverage.get("error_count") == 0,
        "captured response": len(predictions) == 1 and predictions[0].get("error") is None and bool(predictions[0].get("answers")),
    }
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        raise SystemExit("probe report verification failed: " + ", ".join(failures))
    print(f"probe report verified: {args.expect_model}")


if __name__ == "__main__":
    main()
