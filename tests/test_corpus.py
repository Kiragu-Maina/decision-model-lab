from __future__ import annotations

import unittest
from dataclasses import replace

from jevbench.corpus import build_corpus
from jevbench.types import ExpectedAnswer
from jevbench.validation import ValidationError, corpus_digest, validate_corpus


class CorpusTests(unittest.TestCase):
    def test_corpus_is_large_and_balanced(self):
        summary = validate_corpus(build_corpus())
        self.assertGreaterEqual(summary["cases"], 80)
        self.assertGreaterEqual(summary["decisions"], 190)
        self.assertEqual(set(summary["primitives"]), {"choice", "noul", "score"})
        self.assertGreaterEqual(len(summary["slices"]), 9)

    def test_corpus_digest_is_deterministic(self):
        self.assertEqual(corpus_digest(build_corpus()), corpus_digest(build_corpus()))

    def test_all_variants_have_a_base_group(self):
        cases = build_corpus()
        base_groups = {case.group_id for case in cases if case.variant == "base"}
        for case in cases:
            if case.variant != "base":
                self.assertIn(case.group_id, base_groups)

    def test_invalid_probability_mass_is_rejected(self):
        case = build_corpus()[0]
        qid = next(iter(case.expected))
        expected = dict(case.expected)
        expected[qid] = ExpectedAnswer({key: 0.2 for key in expected[qid].probabilities})
        with self.assertRaises(ValidationError):
            validate_corpus([replace(case, expected=expected)])

    def test_duplicate_ids_are_rejected(self):
        case = build_corpus()[0]
        with self.assertRaises(ValidationError):
            validate_corpus([case, case])


if __name__ == "__main__":
    unittest.main()

