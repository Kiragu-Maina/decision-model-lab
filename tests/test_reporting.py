from __future__ import annotations

import unittest

from jevbench.backends import OracleBackend
from jevbench.corpus import build_corpus
from jevbench.reporting import comparison_markdown, markdown_report
from jevbench.runner import RunConfig, run_benchmark


class ReportingTests(unittest.TestCase):
    def setUp(self):
        self.report = run_benchmark(
            build_corpus()[:4], OracleBackend(), RunConfig("oracle", "oracle")
        )

    def test_markdown_contains_core_sections(self):
        rendered = markdown_report(self.report)
        self.assertIn("## By slice", rendered)
        self.assertIn("## Stability", rendered)
        self.assertIn("Accuracy: 1.000", rendered)

    def test_comparison_requires_same_corpus(self):
        other = {**self.report, "corpus": {**self.report["corpus"], "digest": "different"}}
        with self.assertRaises(ValueError):
            comparison_markdown([self.report, other])

    def test_comparison_renders_models(self):
        rendered = comparison_markdown([self.report])
        self.assertIn("oracle", rendered)
        self.assertIn("Brier", rendered)


if __name__ == "__main__":
    unittest.main()
