#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from jevbench.corpus import build_corpus
from jevbench.validation import corpus_digest, validate_corpus


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    parser.add_argument("--expect-model", required=True)
    parser.add_argument("--expect-repetitions", required=True, type=int)
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    cases = build_corpus()
    summary = validate_corpus(cases)
    expected_ids = {case.id for case in cases}
    predictions = report.get("predictions", [])
    prediction_ids = [prediction.get("case_id") for prediction in predictions]
    coverage = report.get("metrics", {}).get("coverage", {})
    checks = {
        "schema version": report.get("schema_version") == "1.0",
        "model": report.get("run", {}).get("model") == args.expect_model,
        "repetitions": report.get("run", {}).get("repetitions") == args.expect_repetitions,
        "corpus digest": report.get("corpus", {}).get("digest") == corpus_digest(cases),
        "requested cases": coverage.get("requested_cases") == len(cases),
        "valid cases": coverage.get("valid_cases") == len(cases),
        "valid decisions": coverage.get("valid_decisions") == summary["decisions"],
        "zero errors": coverage.get("error_count") == 0 and not report.get("metrics", {}).get("errors"),
        "prediction IDs": len(prediction_ids) == len(expected_ids) and set(prediction_ids) == expected_ids,
        "prediction errors": all(prediction.get("error") is None for prediction in predictions),
    }
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        raise SystemExit("report verification failed: " + ", ".join(failures))
    print(f"model report verified: {args.expect_model}")


if __name__ == "__main__":
    main()
