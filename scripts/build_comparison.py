#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from jevbench.reporting import comparison_markdown


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("reports", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--markdown", required=True, type=Path)
    args = parser.parse_args()
    reports = [json.loads(path.read_text(encoding="utf-8")) for path in args.reports]
    digests = {report["corpus"]["digest"] for report in reports}
    if len(digests) != 1:
        raise SystemExit("reports use different corpus digests")
    payload = {
        "schema_version": "1.0",
        "corpus_digest": next(iter(digests)),
        "models": [
            {
                "model": report["run"]["model"],
                "summary": report["metrics"]["summary"],
                "performance": report["metrics"]["performance"],
                "coverage": report["metrics"]["coverage"],
            }
            for report in reports
        ],
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown.write_text(comparison_markdown(reports), encoding="utf-8")
    print(f"wrote comparison for {len(reports)} models")


if __name__ == "__main__":
    main()
