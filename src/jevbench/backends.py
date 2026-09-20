from __future__ import annotations

import json
import os
import shlex
import subprocess
import time
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from .types import BenchmarkCase, Prediction


class Backend(ABC):
    thread_safe = True

    @abstractmethod
    def predict(self, case: BenchmarkCase, model: str) -> Prediction:
        raise NotImplementedError


def _prediction_from_response(case: BenchmarkCase, response: dict[str, Any], latency_ms: float, model: str) -> Prediction:
    answers = response.get("answers")
    if not isinstance(answers, dict):
        return Prediction(case.id, model, {}, latency_ms, response, "response has no answers object")
    return Prediction(
        case_id=case.id,
        model=str(response.get("model", model)),
        answers=answers,
        latency_ms=latency_ms,
        raw=response,
    )


class HttpSystemOneBackend(Backend):
    def __init__(self, base_url: str, api_key: str | None = None, timeout: float = 60.0):
        base = base_url.rstrip("/")
        self.url = base if base.endswith("/v1/systemone") else f"{base}/v1/systemone"
        self.api_key = api_key
        self.timeout = timeout

    def predict(self, case: BenchmarkCase, model: str) -> Prediction:
        body = json.dumps(case.request(model), ensure_ascii=False).encode()
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        request = urllib.request.Request(self.url, data=body, headers=headers, method="POST")
        started = time.perf_counter()
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read())
            latency_ms = (time.perf_counter() - started) * 1000
            return _prediction_from_response(case, payload, latency_ms, model)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
            latency_ms = (time.perf_counter() - started) * 1000
            return Prediction(case.id, model, {}, latency_ms, error=f"HTTP backend: {exc}")


class CommandBackend(Backend):
    thread_safe = False

    def __init__(self, command: str, timeout: float = 60.0):
        self.argv = shlex.split(command)
        if not self.argv:
            raise ValueError("command backend requires a non-empty command")
        self.timeout = timeout

    def predict(self, case: BenchmarkCase, model: str) -> Prediction:
        payload = {"case_id": case.id, **case.request(model)}
        started = time.perf_counter()
        try:
            result = subprocess.run(
                self.argv,
                input=json.dumps(payload, ensure_ascii=False),
                text=True,
                capture_output=True,
                timeout=self.timeout,
                check=False,
            )
            latency_ms = (time.perf_counter() - started) * 1000
            if result.returncode:
                error = result.stderr.strip() or f"command exited {result.returncode}"
                return Prediction(case.id, model, {}, latency_ms, error=error)
            response = json.loads(result.stdout)
            return _prediction_from_response(case, response, latency_ms, model)
        except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError) as exc:
            latency_ms = (time.perf_counter() - started) * 1000
            return Prediction(case.id, model, {}, latency_ms, error=f"command backend: {exc}")


class ReplayBackend(Backend):
    def __init__(self, path: str | Path):
        self.records: dict[str, dict[str, Any]] = {}
        with Path(path).open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                record = json.loads(line)
                case_id = record.get("case_id")
                if not isinstance(case_id, str):
                    raise ValueError(f"replay line {line_number} has no case_id")
                if case_id in self.records:
                    raise ValueError(f"duplicate replay case_id: {case_id}")
                self.records[case_id] = record

    def predict(self, case: BenchmarkCase, model: str) -> Prediction:
        record = self.records.get(case.id)
        if record is None:
            return Prediction(case.id, model, {}, -1, error="case missing from replay")
        response = record.get("response", record)
        latency_ms = float(record.get("latency_ms", response.get("latency_ms", -1)))
        return _prediction_from_response(case, response, latency_ms, model)


class OracleBackend(Backend):
    """Deterministic perfect backend for testing the harness, never for model comparison."""

    def predict(self, case: BenchmarkCase, model: str) -> Prediction:
        answers: dict[str, dict[str, Any]] = {}
        for qid, question in case.questions.items():
            probabilities = dict(case.expected[qid].probabilities)
            selected = max(probabilities, key=probabilities.__getitem__)
            if question.type == "noul":
                answers[qid] = {"type": "noul", "noul": probabilities["true"]}
            elif question.type == "choice":
                answers[qid] = {
                    "type": "choice",
                    "choice": selected,
                    "probabilities": probabilities,
                    "confidence": max(probabilities.values()),
                }
            else:
                answers[qid] = {
                    "type": "score",
                    "score": sum(float(key) * value for key, value in probabilities.items()),
                    "probabilities": probabilities,
                    "confidence": max(probabilities.values()),
                }
        response = {"model": model, "answers": answers, "usage": {"input_tokens": 0, "output_tokens": 0}}
        return Prediction(case.id, model, answers, 1.0, response)


def backend_from_config(
    kind: str,
    *,
    base_url: str | None = None,
    api_key: str | None = None,
    command: str | None = None,
    replay: str | None = None,
    timeout: float = 60.0,
) -> Backend:
    if kind == "http":
        resolved_url = base_url or os.environ.get("JEVBENCH_BASE_URL")
        if not resolved_url:
            raise ValueError("HTTP backend requires --base-url or JEVBENCH_BASE_URL")
        return HttpSystemOneBackend(resolved_url, api_key=api_key, timeout=timeout)
    if kind == "command":
        if not command:
            raise ValueError("command backend requires --command")
        return CommandBackend(command, timeout=timeout)
    if kind == "replay":
        if not replay:
            raise ValueError("replay backend requires --replay")
        return ReplayBackend(replay)
    if kind == "oracle":
        return OracleBackend()
    raise ValueError(f"unknown backend: {kind}")

