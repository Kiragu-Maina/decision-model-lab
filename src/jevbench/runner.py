from __future__ import annotations

import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .backends import Backend
from .corpus import CORPUS_VERSION
from .metrics import calculate_metrics
from .types import BenchmarkCase, Prediction
from .validation import corpus_digest, validate_corpus


@dataclass(frozen=True)
class RunConfig:
    model: str
    backend_name: str
    repetitions: int = 1
    concurrency: int = 1


def _predict_repeated(backend: Backend, case: BenchmarkCase, config: RunConfig) -> Prediction:
    attempts = [backend.predict(case, config.model) for _ in range(config.repetitions)]
    valid_latencies = [attempt.latency_ms for attempt in attempts if attempt.latency_ms >= 0]
    selected = next((attempt for attempt in reversed(attempts) if not attempt.error), attempts[-1])
    if valid_latencies:
        selected.latency_ms = statistics.median(valid_latencies)
    return selected


def run_benchmark(cases: list[BenchmarkCase], backend: Backend, config: RunConfig) -> dict[str, Any]:
    if config.repetitions < 1:
        raise ValueError("repetitions must be at least one")
    if config.concurrency < 1:
        raise ValueError("concurrency must be at least one")
    corpus_summary = validate_corpus(cases)
    concurrency = config.concurrency if backend.thread_safe else 1
    started = time.perf_counter()
    if concurrency == 1:
        predictions = [_predict_repeated(backend, case, config) for case in cases]
    else:
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            predictions = list(executor.map(lambda case: _predict_repeated(backend, case, config), cases))
    wall_time_ms = (time.perf_counter() - started) * 1000
    metrics = calculate_metrics(cases, predictions, wall_time_ms=wall_time_ms)
    return {
        "schema_version": "1.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "corpus": {
            "version": CORPUS_VERSION,
            "digest": corpus_digest(cases),
            **corpus_summary,
        },
        "run": {
            "model": config.model,
            "backend": config.backend_name,
            "repetitions": config.repetitions,
            "requested_concurrency": config.concurrency,
            "effective_concurrency": concurrency,
        },
        "metrics": metrics,
        "predictions": [
            {
                "case_id": prediction.case_id,
                "model": prediction.model,
                "latency_ms": prediction.latency_ms,
                "answers": prediction.answers,
                "error": prediction.error,
            }
            for prediction in predictions
        ],
    }
