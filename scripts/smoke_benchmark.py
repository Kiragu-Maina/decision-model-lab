from __future__ import annotations

import json
import tempfile
from pathlib import Path

from jevbench.backends import OracleBackend
from jevbench.corpus import build_corpus
from jevbench.reporting import markdown_report, write_json_report, write_markdown_report
from jevbench.runner import RunConfig, run_benchmark


def main() -> None:
    cases = build_corpus()
    report = run_benchmark(cases, OracleBackend(), RunConfig("oracle", "oracle", concurrency=4))
    metrics = report["metrics"]
    assert metrics["coverage"]["error_count"] == 0
    assert metrics["coverage"]["valid_cases"] == len(cases)
    assert metrics["summary"]["accuracy"] == 1.0
    assert metrics["summary"]["brier"] == 0.0
    assert all(row["selection_agreement"] == 1.0 for row in metrics["stability"].values())
    assert all(row["mean_tv_distance"] == 0.0 for row in metrics["stability"].values())
    with tempfile.TemporaryDirectory() as directory:
        json_path = Path(directory) / "report.json"
        markdown_path = Path(directory) / "report.md"
        write_json_report(report, json_path)
        write_markdown_report(report, markdown_path)
        loaded = json.loads(json_path.read_text(encoding="utf-8"))
        assert loaded["corpus"]["digest"] == report["corpus"]["digest"]
        rendered = markdown_path.read_text(encoding="utf-8")
        assert "# jevbench report: oracle" in rendered
        assert rendered == markdown_report(report)
    print("smoke benchmark passed")


if __name__ == "__main__":
    main()

