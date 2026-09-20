from __future__ import annotations

import unittest

from jevbench.backends import OracleBackend
from jevbench.corpus import build_corpus
from jevbench.metrics import calculate_metrics
from jevbench.runner import RunConfig, run_benchmark
from jevbench.types import Prediction


class MetricsTests(unittest.TestCase):
    def setUp(self):
        self.cases = build_corpus()

    def test_oracle_scores_perfectly(self):
        report = run_benchmark(self.cases, OracleBackend(), RunConfig("oracle", "oracle"))
        metrics = report["metrics"]
        self.assertEqual(metrics["summary"]["accuracy"], 1.0)
        self.assertEqual(metrics["summary"]["brier"], 0.0)
        self.assertEqual(metrics["coverage"]["error_count"], 0)

    def test_oracle_is_stable_across_all_perturbations(self):
        report = run_benchmark(self.cases, OracleBackend(), RunConfig("oracle", "oracle"))
        stability = report["metrics"]["stability"]
        self.assertEqual(
            set(stability), {"irrelevant_context", "option_order", "paraphrase", "question_order"}
        )
        for row in stability.values():
            self.assertEqual(row["selection_agreement"], 1.0)
            self.assertEqual(row["mean_tv_distance"], 0.0)

    def test_missing_predictions_are_reported(self):
        metrics = calculate_metrics(self.cases[:2], [])
        self.assertEqual(metrics["coverage"]["error_count"], 2)
        self.assertEqual(metrics["coverage"]["valid_cases"], 0)

    def test_malformed_answer_is_reported(self):
        case = self.cases[0]
        prediction = Prediction(case.id, "bad", {"unknown": {}}, 1.0)
        metrics = calculate_metrics([case], [prediction])
        self.assertEqual(metrics["coverage"]["error_count"], 1)

    def test_repetitions_use_median_latency(self):
        report = run_benchmark(
            self.cases[:1], OracleBackend(), RunConfig("oracle", "oracle", repetitions=3)
        )
        self.assertEqual(report["metrics"]["performance"]["p50_ms"], 1.0)


if __name__ == "__main__":
    unittest.main()

