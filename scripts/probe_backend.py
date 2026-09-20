#!/usr/bin/env python3
from __future__ import annotations

import argparse

from jevbench.backends import HttpSystemOneBackend
from jevbench.corpus import build_corpus
from jevbench.validation import normalize_prediction


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--expect-model", required=True)
    args = parser.parse_args()
    case = build_corpus()[0]
    prediction = HttpSystemOneBackend(args.base_url, timeout=180).predict(case, args.expect_model)
    if prediction.error:
        raise SystemExit(prediction.error)
    if prediction.model != args.expect_model:
        raise SystemExit(f"model mismatch: {prediction.model!r}")
    normalize_prediction(case, prediction)
    print(f"backend probe passed: {args.expect_model}")


if __name__ == "__main__":
    main()
