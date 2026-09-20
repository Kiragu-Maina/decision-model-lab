from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

QuestionType = Literal["choice", "noul", "score"]


@dataclass(frozen=True)
class Question:
    type: QuestionType
    instructions: str
    criteria: dict[str, Any] | list[str] | None = None

    def option_ids(self) -> tuple[str, ...]:
        if self.type == "noul":
            return ("false", "true")
        if self.type == "choice":
            assert isinstance(self.criteria, dict)
            return tuple(self.criteria)
        assert isinstance(self.criteria, list)
        return tuple(str(i) for i in range(len(self.criteria)))

    def as_request(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "type": self.type,
            "instructions": self.instructions,
        }
        if self.criteria is not None:
            result["criteria"] = self.criteria
        return result


@dataclass(frozen=True)
class ExpectedAnswer:
    probabilities: dict[str, float]

    @property
    def selected(self) -> str:
        return max(self.probabilities, key=self.probabilities.__getitem__)

    @property
    def expected_score(self) -> float:
        return sum(float(key) * value for key, value in self.probabilities.items())


@dataclass(frozen=True)
class BenchmarkCase:
    id: str
    slice: str
    state: Any
    questions: dict[str, Question]
    expected: dict[str, ExpectedAnswer]
    tags: tuple[str, ...] = ()
    group_id: str | None = None
    variant: str = "base"
    metadata: dict[str, Any] = field(default_factory=dict)

    def request(self, model: str) -> dict[str, Any]:
        return {
            "model": model,
            "state": self.state,
            "questions": {key: value.as_request() for key, value in self.questions.items()},
        }


@dataclass
class Prediction:
    case_id: str
    model: str
    answers: dict[str, dict[str, Any]]
    latency_ms: float
    raw: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

