from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from typing import Any

from .types import BenchmarkCase, Prediction


class ValidationError(ValueError):
    pass


def _canonical_case(case: BenchmarkCase) -> dict[str, Any]:
    return {
        "id": case.id,
        "slice": case.slice,
        "state": case.state,
        "questions": {qid: question.as_request() for qid, question in case.questions.items()},
        "expected": {qid: answer.probabilities for qid, answer in case.expected.items()},
        "tags": list(case.tags),
        "group_id": case.group_id,
        "variant": case.variant,
        "metadata": case.metadata,
    }


def corpus_digest(cases: list[BenchmarkCase]) -> str:
    payload = json.dumps(
        [_canonical_case(case) for case in cases],
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return hashlib.sha256(payload).hexdigest()


def validate_corpus(cases: list[BenchmarkCase]) -> dict[str, Any]:
    if not cases:
        raise ValidationError("corpus is empty")
    ids = [case.id for case in cases]
    duplicates = [key for key, count in Counter(ids).items() if count > 1]
    if duplicates:
        raise ValidationError(f"duplicate case ids: {duplicates}")

    decisions = 0
    primitives: Counter[str] = Counter()
    slices: Counter[str] = Counter()
    variants: Counter[str] = Counter()
    soft_targets = 0
    for case in cases:
        if not case.id or not case.slice:
            raise ValidationError("case id and slice must be non-empty")
        if not case.questions:
            raise ValidationError(f"{case.id}: no questions")
        if set(case.questions) != set(case.expected):
            raise ValidationError(f"{case.id}: expected answers do not match question ids")
        slices[case.slice] += 1
        variants[case.variant] += 1
        for qid, question in case.questions.items():
            decisions += 1
            primitives[question.type] += 1
            options = question.option_ids()
            if len(options) < 2:
                raise ValidationError(f"{case.id}/{qid}: fewer than two options")
            if len(set(options)) != len(options):
                raise ValidationError(f"{case.id}/{qid}: duplicate options")
            probabilities = case.expected[qid].probabilities
            if set(probabilities) != set(options):
                raise ValidationError(
                    f"{case.id}/{qid}: probability keys {sorted(probabilities)} "
                    f"do not match options {sorted(options)}"
                )
            if any(not math.isfinite(value) or value < 0 or value > 1 for value in probabilities.values()):
                raise ValidationError(f"{case.id}/{qid}: invalid probability")
            if not math.isclose(sum(probabilities.values()), 1.0, abs_tol=1e-8):
                raise ValidationError(f"{case.id}/{qid}: probabilities do not sum to one")
            if max(probabilities.values()) < 1.0:
                soft_targets += 1

    return {
        "cases": len(cases),
        "decisions": decisions,
        "slices": dict(sorted(slices.items())),
        "primitives": dict(sorted(primitives.items())),
        "variants": dict(sorted(variants.items())),
        "soft_targets": soft_targets,
        "digest": corpus_digest(cases),
    }


def normalize_answer(case: BenchmarkCase, qid: str, answer: dict[str, Any]) -> dict[str, Any]:
    question = case.questions[qid]
    options = question.option_ids()
    if question.type == "noul":
        if "noul" in answer:
            p_true = float(answer["noul"])
            probabilities = {"false": 1.0 - p_true, "true": p_true}
        else:
            probabilities = {key: float(value) for key, value in answer.get("probabilities", {}).items()}
    else:
        probabilities = {str(key): float(value) for key, value in answer.get("probabilities", {}).items()}
    if set(probabilities) != set(options):
        raise ValidationError(
            f"{case.id}/{qid}: response probabilities {sorted(probabilities)} "
            f"do not match options {sorted(options)}"
        )
    if any(not math.isfinite(value) or value < 0 for value in probabilities.values()):
        raise ValidationError(f"{case.id}/{qid}: response contains invalid probability")
    total = sum(probabilities.values())
    if total <= 0:
        raise ValidationError(f"{case.id}/{qid}: response probability mass is zero")
    normalized = {key: value / total for key, value in probabilities.items()}
    selected = max(normalized, key=normalized.__getitem__)
    if question.type == "choice" and answer.get("choice") is not None:
        declared = str(answer["choice"])
        if declared not in options:
            raise ValidationError(f"{case.id}/{qid}: declared choice is outside the schema")
        selected = declared
    expected_score = sum(float(key) * value for key, value in normalized.items()) if question.type == "score" else None
    return {
        "type": question.type,
        "probabilities": normalized,
        "selected": selected,
        "confidence": max(normalized.values()),
        "score": expected_score,
    }


def normalize_prediction(case: BenchmarkCase, prediction: Prediction) -> dict[str, dict[str, Any]]:
    if prediction.error:
        raise ValidationError(prediction.error)
    if set(prediction.answers) != set(case.questions):
        missing = sorted(set(case.questions) - set(prediction.answers))
        extra = sorted(set(prediction.answers) - set(case.questions))
        raise ValidationError(f"{case.id}: answer ids mismatch; missing={missing}, extra={extra}")
    return {qid: normalize_answer(case, qid, prediction.answers[qid]) for qid in case.questions}

