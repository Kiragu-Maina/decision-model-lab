"""TypeSafe-compatible HTTP bridge for SemIf's native Apple-Silicon scorer.

The process loads the model once and answers every request with one shared-state
MLX batch. Run this on macOS; Docker is intentionally reserved for jevbench.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

MODEL_LABEL = "semif-qwen3.5-4b-mlx"
MAX_BODY_BYTES = 2 * 1024 * 1024


def render(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def option_text(name: str, description: Any) -> str:
    rendered = render(description) if description is not None else ""
    return name if not rendered else f"{name}: {rendered}"


def request_rows(payload: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if "state" not in payload or not payload.get("questions"):
        raise ValueError("request requires state and at least one question")
    if not isinstance(payload["questions"], dict):
        raise ValueError("questions must be an object")
    rows: list[dict[str, Any]] = []
    mappings: list[dict[str, Any]] = []
    for qid, question in payload["questions"].items():
        if not isinstance(qid, str) or not isinstance(question, dict):
            raise ValueError("question IDs must be strings and questions must be objects")
        kind = question.get("type")
        instructions = render(question.get("instructions", ""))
        criteria = question.get("criteria")
        if kind == "noul":
            criteria = criteria if isinstance(criteria, dict) else {}
            ids = ["false", "true"]
            options = [
                {"id": "false", "description": option_text("no", criteria.get("false"))},
                {"id": "true", "description": option_text("yes", criteria.get("true"))},
            ]
            mapping = {"id": qid, "type": kind, "ids": ids}
        elif kind == "choice":
            if not isinstance(criteria, dict) or len(criteria) < 2:
                raise ValueError(f"{qid}: choice criteria must contain at least two options")
            ids = list(criteria)
            options = [
                {"id": key, "description": option_text(key, criteria[key])}
                for key in ids
            ]
            mapping = {"id": qid, "type": kind, "ids": ids}
        elif kind == "score":
            if not isinstance(criteria, list) or len(criteria) < 2:
                raise ValueError(f"{qid}: score criteria must contain at least two levels")
            ids = [str(index) for index in range(len(criteria))]
            options = [
                {"id": key, "description": option_text(key, description)}
                for key, description in zip(ids, criteria)
            ]
            mapping = {
                "id": qid,
                "type": kind,
                "ids": ids,
                "legend": {key: render(value) for key, value in zip(ids, criteria)},
            }
        else:
            raise ValueError(f"{qid}: unsupported question type {kind!r}")
        rows.append({"id": qid, "state": payload["state"], "question": instructions, "options": options})
        mappings.append(mapping)
    return rows, mappings


def response_answers(results: list[dict[str, Any]], mappings: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    answers: dict[str, dict[str, Any]] = {}
    for result, mapping in zip(results, mappings, strict=True):
        probabilities = [float(value) for value in result["probabilities"]]
        if len(probabilities) != len(mapping["ids"]) or any(not math.isfinite(value) for value in probabilities):
            raise ValueError(f"{mapping['id']}: scorer returned an invalid distribution")
        distribution = dict(zip(mapping["ids"], probabilities, strict=True))
        selected = max(distribution, key=distribution.__getitem__)
        if mapping["type"] == "noul":
            answer = {"type": "noul", "noul": distribution["true"]}
        elif mapping["type"] == "choice":
            answer = {
                "type": "choice",
                "choice": selected,
                "confidence": distribution[selected],
                "probabilities": distribution,
            }
        else:
            answer = {
                "type": "score",
                "score": sum(float(key) * value for key, value in distribution.items()),
                "confidence": distribution[selected],
                "legend": mapping["legend"],
                "probabilities": distribution,
            }
        answers[mapping["id"]] = answer
    return answers


class SemIfService:
    def __init__(self, source: str, revision: str, bits: int | None, max_tokens: int, cache_limit_mib: int):
        from semif_phase1 import mlx_backend

        self.source = source
        self.revision = revision
        self.bits = bits
        self.max_tokens = max_tokens
        self.model, self.tokenizer, self.metadata = mlx_backend.load_model(
            source, revision, bits, cache_limit_mib=cache_limit_mib
        )
        self._score_shared = mlx_backend.score_shared

    def predict(self, payload: dict[str, Any]) -> dict[str, Any]:
        started = time.perf_counter()
        rows, mappings = request_rows(payload)
        results, timing = self._score_shared(
            self.model, self.tokenizer, rows, self.metadata, self.max_tokens
        )
        answers = response_answers(results, mappings)
        return {
            "model": str(payload.get("model", MODEL_LABEL)),
            "answers": answers,
            "usage": {
                "input_tokens": sum(int(result["input_tokens"]) for result in results),
                "output_tokens": 0,
            },
            "latency_ms": (time.perf_counter() - started) * 1000,
            "semif": {
                "source": self.source,
                "revision": self.revision,
                "backend": "mlx",
                "mode": "shared",
                "bits": self.bits,
                "timing": timing,
            },
        }


def make_handler(service: SemIfService):
    class Handler(BaseHTTPRequestHandler):
        server_version = "SemIfBridge/1.0"

        def log_message(self, fmt: str, *args: Any) -> None:
            print(f"{self.address_string()} - {fmt % args}", flush=True)

        def send_json(self, status: int, payload: dict[str, Any]) -> None:
            body = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802
            if self.path == "/v1/models":
                self.send_json(200, {"models": [{"id": MODEL_LABEL, "source": service.source, "revision": service.revision}]})
            else:
                self.send_json(404, {"error": "not found"})

        def do_POST(self) -> None:  # noqa: N802
            if self.path != "/v1/systemone":
                self.send_json(404, {"error": "not found"})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length < 2 or length > MAX_BODY_BYTES:
                    raise ValueError("invalid request size")
                payload = json.loads(self.rfile.read(length))
                if not isinstance(payload, dict):
                    raise ValueError("request body must be an object")
                self.send_json(200, service.predict(payload))
            except (json.JSONDecodeError, TypeError, ValueError) as error:
                self.send_json(422, {"error": str(error)})
            except Exception as error:  # keep one bad request from stopping a long benchmark
                self.send_json(500, {"error": f"inference failed: {type(error).__name__}: {error}"})

    return Handler


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="Qwen/Qwen3.5-4B")
    parser.add_argument("--revision", default="851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a")
    parser.add_argument("--bits", type=int, choices=(4, 8))
    parser.add_argument("--max-tokens", type=int, default=4096)
    parser.add_argument("--cache-limit-mib", type=int, default=256)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8011)
    args = parser.parse_args()
    service = SemIfService(args.model, args.revision, args.bits, args.max_tokens, args.cache_limit_mib)
    server = HTTPServer((args.host, args.port), make_handler(service))
    print(
        f"serving {MODEL_LABEL} ({args.model}@{args.revision}, bits={args.bits or 'source'}) "
        f"on http://{args.host}:{args.port}",
        flush=True,
    )
    server.serve_forever()


if __name__ == "__main__":
    main()
