from __future__ import annotations

import math
import statistics
from collections import Counter, defaultdict
from typing import Any

from .types import BenchmarkCase, Prediction
from .validation import ValidationError, normalize_prediction

EPSILON = 1e-12


def _brier(predicted: dict[str, float], gold: dict[str, float]) -> float:
    return sum((predicted[key] - gold[key]) ** 2 for key in gold)


def _cross_entropy(predicted: dict[str, float], gold: dict[str, float]) -> float:
    return -sum(target * math.log(max(predicted[key], EPSILON)) for key, target in gold.items())


def _tv(left: dict[str, float], right: dict[str, float]) -> float:
    return 0.5 * sum(abs(left[key] - right[key]) for key in left)


def _percentile(values: list[float], quantile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = (len(ordered) - 1) * quantile
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return ordered[lower]
    weight = index - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def _ece(rows: list[dict[str, Any]], bins: int = 10) -> float | None:
    if not rows:
        return None
    total = len(rows)
    error = 0.0
    for bucket in range(bins):
        low = bucket / bins
        high = (bucket + 1) / bins
        members = [
            row for row in rows
            if row["confidence"] >= low and (row["confidence"] < high or (bucket == bins - 1 and row["confidence"] <= high))
        ]
        if not members:
            continue
        accuracy = statistics.fmean(row["calibration_target"] for row in members)
        confidence = statistics.fmean(row["confidence"] for row in members)
        error += len(members) / total * abs(accuracy - confidence)
    return error


def _aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"count": 0}
    result: dict[str, Any] = {
        "count": len(rows),
        "accuracy": statistics.fmean(row["correct"] for row in rows),
        "soft_accuracy": statistics.fmean(row["soft_accuracy"] for row in rows),
        "brier": statistics.fmean(row["brier"] for row in rows),
        "log_loss": statistics.fmean(row["log_loss"] for row in rows),
        "ece": _ece(rows),
    }
    score_rows = [row for row in rows if row["primitive"] == "score"]
    result["score_mae"] = statistics.fmean(row["score_mae"] for row in score_rows) if score_rows else None
    return result


def calculate_metrics(
    cases: list[BenchmarkCase],
    predictions: list[Prediction],
    *,
    wall_time_ms: float | None = None,
) -> dict[str, Any]:
    prediction_by_id = {prediction.case_id: prediction for prediction in predictions}
    rows: list[dict[str, Any]] = []
    normalized_by_case: dict[str, dict[str, dict[str, Any]]] = {}
    errors: list[dict[str, str]] = []
    latencies: list[float] = []

    for case in cases:
        prediction = prediction_by_id.get(case.id)
        if prediction is None:
            errors.append({"case_id": case.id, "error": "missing prediction"})
            continue
        if prediction.latency_ms >= 0:
            latencies.append(prediction.latency_ms)
        try:
            normalized = normalize_prediction(case, prediction)
        except (ValidationError, TypeError, ValueError) as exc:
            errors.append({"case_id": case.id, "error": str(exc)})
            continue
        normalized_by_case[case.id] = normalized
        for qid, answer in normalized.items():
            gold = case.expected[qid].probabilities
            selected = answer["selected"]
            gold_selected = max(gold, key=gold.__getitem__)
            question = case.questions[qid]
            score_mae = None
            if question.type == "score":
                gold_score = sum(float(key) * value for key, value in gold.items())
                score_mae = abs(float(answer["score"]) - gold_score)
            rows.append(
                {
                    "case_id": case.id,
                    "question_id": qid,
                    "slice": case.slice,
                    "variant": case.variant,
                    "primitive": question.type,
                    "selected": selected,
                    "gold_selected": gold_selected,
                    "correct": float(selected == gold_selected),
                    "calibration_target": gold[selected],
                    "confidence": answer["confidence"],
                    "soft_accuracy": sum(answer["probabilities"][key] * value for key, value in gold.items()),
                    "brier": _brier(answer["probabilities"], gold),
                    "log_loss": _cross_entropy(answer["probabilities"], gold),
                    "score_mae": score_mae,
                }
            )

    by_slice: dict[str, Any] = {}
    for slice_name in sorted({row["slice"] for row in rows}):
        by_slice[slice_name] = _aggregate([row for row in rows if row["slice"] == slice_name])
    by_primitive: dict[str, Any] = {}
    for primitive in ("choice", "noul", "score"):
        by_primitive[primitive] = _aggregate([row for row in rows if row["primitive"] == primitive])

    pair_rows: list[dict[str, Any]] = []
    groups: dict[str, list[BenchmarkCase]] = defaultdict(list)
    for case in cases:
        if case.group_id:
            groups[case.group_id].append(case)
    for group_id, members in groups.items():
        base = next((case for case in members if case.variant == "base"), None)
        if base is None or base.id not in normalized_by_case:
            continue
        for variant in members:
            if variant.variant == "base" or variant.id not in normalized_by_case:
                continue
            common = set(base.questions) & set(variant.questions)
            for qid in common:
                left = normalized_by_case[base.id][qid]
                right = normalized_by_case[variant.id][qid]
                pair_rows.append(
                    {
                        "group_id": group_id,
                        "question_id": qid,
                        "variant": variant.variant,
                        "same_selection": float(left["selected"] == right["selected"]),
                        "tv_distance": _tv(left["probabilities"], right["probabilities"]),
                    }
                )
    stability: dict[str, Any] = {}
    for variant in sorted({row["variant"] for row in pair_rows}):
        subset = [row for row in pair_rows if row["variant"] == variant]
        stability[variant] = {
            "count": len(subset),
            "selection_agreement": statistics.fmean(row["same_selection"] for row in subset),
            "mean_tv_distance": statistics.fmean(row["tv_distance"] for row in subset),
            "max_tv_distance": max(row["tv_distance"] for row in subset),
        }

    selective: dict[str, Any] = {}
    for threshold in (0.5, 0.7, 0.9):
        accepted = [row for row in rows if row["confidence"] >= threshold]
        selective[str(threshold)] = {
            "coverage": len(accepted) / len(rows) if rows else 0.0,
            "accuracy": statistics.fmean(row["correct"] for row in accepted) if accepted else None,
            "accepted": len(accepted),
        }

    total_duration_ms = wall_time_ms if wall_time_ms is not None else sum(latencies)
    return {
        "summary": _aggregate(rows),
        "by_slice": by_slice,
        "by_primitive": by_primitive,
        "stability": stability,
        "selective": selective,
        "performance": {
            "case_count": len(latencies),
            "p50_ms": _percentile(latencies, 0.5),
            "p95_ms": _percentile(latencies, 0.95),
            "mean_ms": statistics.fmean(latencies) if latencies else None,
            "throughput_cases_per_second": (1000 * len(latencies) / total_duration_ms) if total_duration_ms > 0 else None,
            "wall_time_ms": wall_time_ms,
            "summed_request_latency_ms": sum(latencies),
        },
        "coverage": {
            "requested_cases": len(cases),
            "valid_cases": len(normalized_by_case),
            "valid_decisions": len(rows),
            "error_count": len(errors),
        },
        "errors": errors,
        "rows": rows,
    }
