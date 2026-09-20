from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_json_report(report: dict[str, Any], path: str | Path) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def markdown_report(report: dict[str, Any]) -> str:
    metrics = report["metrics"]
    summary = metrics["summary"]
    performance = metrics["performance"]
    coverage = metrics["coverage"]
    lines = [
        f"# jevbench report: {report['run']['model']}",
        "",
        f"- Corpus: `{report['corpus']['version']}` (`{report['corpus']['digest'][:12]}`)",
        f"- Backend: `{report['run']['backend']}`",
        f"- Valid cases: {coverage['valid_cases']}/{coverage['requested_cases']}",
        f"- Accuracy: {_fmt(summary.get('accuracy'))}",
        f"- Soft accuracy: {_fmt(summary.get('soft_accuracy'))}",
        f"- Brier score: {_fmt(summary.get('brier'))}",
        f"- ECE: {_fmt(summary.get('ece'))}",
        f"- Latency p50/p95: {_fmt(performance.get('p50_ms'), 1)} / {_fmt(performance.get('p95_ms'), 1)} ms",
        "",
        "## By slice",
        "",
        "| Slice | N | Accuracy | Brier | ECE |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, row in metrics["by_slice"].items():
        lines.append(
            f"| {name} | {row['count']} | {_fmt(row.get('accuracy'))} | "
            f"{_fmt(row.get('brier'))} | {_fmt(row.get('ece'))} |"
        )
    lines.extend(["", "## Stability", "", "| Variant | Pairs | Selection agreement | Mean TV |", "|---|---:|---:|---:|"])
    for name, row in metrics["stability"].items():
        lines.append(
            f"| {name} | {row['count']} | {_fmt(row['selection_agreement'])} | {_fmt(row['mean_tv_distance'])} |"
        )
    if metrics["errors"]:
        lines.extend(["", "## Errors", ""])
        for error in metrics["errors"]:
            lines.append(f"- `{error['case_id']}`: {error['error']}")
    lines.append("")
    return "\n".join(lines)


def write_markdown_report(report: dict[str, Any], path: str | Path) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(markdown_report(report), encoding="utf-8")


def comparison_markdown(reports: list[dict[str, Any]]) -> str:
    lines = [
        "# jevbench comparison",
        "",
        "| Model | Accuracy | Soft accuracy | Brier ↓ | ECE ↓ | p50 ms ↓ | Errors |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    digests = {report["corpus"]["digest"] for report in reports}
    if len(digests) != 1:
        raise ValueError("cannot compare reports from different corpus digests")
    for report in reports:
        summary = report["metrics"]["summary"]
        performance = report["metrics"]["performance"]
        coverage = report["metrics"]["coverage"]
        lines.append(
            f"| {report['run']['model']} | {_fmt(summary.get('accuracy'))} | "
            f"{_fmt(summary.get('soft_accuracy'))} | {_fmt(summary.get('brier'))} | "
            f"{_fmt(summary.get('ece'))} | {_fmt(performance.get('p50_ms'), 1)} | "
            f"{coverage['error_count']} |"
        )
    lines.append("")
    return "\n".join(lines)

