from __future__ import annotations

from dataclasses import replace

from jevbench.corpus import build_corpus
from jevbench.types import ExpectedAnswer
from jevbench.validation import ValidationError, validate_corpus


def main() -> None:
    cases = build_corpus()
    summary = validate_corpus(cases)
    assert summary["cases"] >= 80, summary
    assert summary["decisions"] >= 190, summary
    assert set(summary["primitives"]) == {"choice", "noul", "score"}, summary
    assert len(summary["slices"]) >= 9, summary
    assert min(summary["slices"].values()) >= 6, summary
    assert summary["soft_targets"] >= 15, summary
    for variant in ("option_order", "question_order", "paraphrase", "irrelevant_context"):
        assert summary["variants"].get(variant, 0) >= 8, summary

    positive = cases[0]
    first_qid = next(iter(positive.expected))
    broken_expected = dict(positive.expected)
    broken_expected[first_qid] = ExpectedAnswer(
        {key: 0.0 for key in positive.expected[first_qid].probabilities}
    )
    invalid = [replace(positive, id="known-invalid", expected=broken_expected)]
    try:
        validate_corpus(invalid)
    except ValidationError:
        pass
    else:
        raise AssertionError("validator accepted the known-invalid probability control")
    print("corpus verification passed")


if __name__ == "__main__":
    main()

