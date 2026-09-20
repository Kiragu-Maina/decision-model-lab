from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .backends import backend_from_config
from .corpus import CORPUS_VERSION, build_corpus
from .reporting import comparison_markdown, markdown_report, write_json_report, write_markdown_report
from .runner import RunConfig, run_benchmark
from .validation import validate_corpus


def _select_cases(args: argparse.Namespace):
    cases = build_corpus()
    if getattr(args, "slice", None):
        selected = set(args.slice)
        cases = [case for case in cases if case.slice in selected]
    if getattr(args, "base_only", False):
        cases = [case for case in cases if case.variant == "base"]
    if getattr(args, "limit", None):
        cases = cases[: args.limit]
    return cases


def _cmd_validate(args: argparse.Namespace) -> int:
    summary = validate_corpus(_select_cases(args))
    print(json.dumps({"corpus_version": CORPUS_VERSION, **summary}, indent=2, sort_keys=True))
    return 0


def _cmd_dry_run(args: argparse.Namespace) -> int:
    cases = _select_cases(args)
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as handle:
        for case in cases:
            handle.write(json.dumps({"case_id": case.id, **case.request(args.model)}, ensure_ascii=False) + "\n")
    print(f"wrote {len(cases)} requests to {destination}")
    return 0


def _cmd_run(args: argparse.Namespace) -> int:
    cases = _select_cases(args)
    api_key = args.api_key or (os.environ.get(args.api_key_env) if args.api_key_env else None)
    backend = backend_from_config(
        args.backend,
        base_url=args.base_url,
        api_key=api_key,
        command=args.command,
        replay=args.replay,
        timeout=args.timeout,
    )
    report = run_benchmark(
        cases,
        backend,
        RunConfig(
            model=args.model,
            backend_name=args.backend,
            repetitions=args.repetitions,
            concurrency=args.concurrency,
        ),
    )
    write_json_report(report, args.output)
    markdown_path = args.markdown or str(Path(args.output).with_suffix(".md"))
    write_markdown_report(report, markdown_path)
    print(markdown_report(report))
    return 0 if report["metrics"]["coverage"]["error_count"] == 0 else 2


def _cmd_compare(args: argparse.Namespace) -> int:
    reports = [json.loads(Path(path).read_text(encoding="utf-8")) for path in args.reports]
    rendered = comparison_markdown(reports)
    if args.output:
        destination = Path(args.output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8")
    print(rendered)
    return 0


def _add_selection(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--slice", action="append", help="include only this slice; repeatable")
    parser.add_argument("--base-only", action="store_true", help="exclude paired perturbation variants")
    parser.add_argument("--limit", type=int, help="run only the first N selected cases")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="jevbench", description="Benchmark typed decision models")
    subparsers = parser.add_subparsers(dest="command_name", required=True)

    validate = subparsers.add_parser("validate", help="validate and summarize the corpus")
    _add_selection(validate)
    validate.set_defaults(func=_cmd_validate)

    dry_run = subparsers.add_parser("dry-run", help="write provider-ready requests without inference")
    _add_selection(dry_run)
    dry_run.add_argument("--model", default=os.environ.get("JEVBENCH_MODEL", "local"))
    dry_run.add_argument("--output", default="reports/requests.jsonl")
    dry_run.set_defaults(func=_cmd_dry_run)

    run = subparsers.add_parser("run", help="execute the benchmark")
    _add_selection(run)
    run.add_argument("--backend", choices=("http", "command", "replay", "oracle"), default="http")
    run.add_argument("--model", default=os.environ.get("JEVBENCH_MODEL", "local"))
    run.add_argument("--base-url", default=os.environ.get("JEVBENCH_BASE_URL"))
    run.add_argument("--api-key")
    run.add_argument("--api-key-env", default="JEVBENCH_API_KEY")
    run.add_argument("--command", help="adapter executable; reads one request on stdin and writes one response")
    run.add_argument("--replay", help="JSONL replay file")
    run.add_argument("--timeout", type=float, default=60.0)
    run.add_argument("--repetitions", type=int, default=1)
    run.add_argument("--concurrency", type=int, default=1)
    run.add_argument("--output", default="reports/result.json")
    run.add_argument("--markdown")
    run.set_defaults(func=_cmd_run)

    compare = subparsers.add_parser("compare", help="compare compatible JSON reports")
    compare.add_argument("reports", nargs="+")
    compare.add_argument("--output")
    compare.set_defaults(func=_cmd_compare)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
