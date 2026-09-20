from __future__ import annotations

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from adapters.semif_server import request_rows, response_answers


class SemIfAdapterTests(unittest.TestCase):
    def test_all_question_types_round_trip(self) -> None:
        payload = {
            "state": {"ticket": "charged twice"},
            "questions": {
                "urgent": {"type": "noul", "instructions": "Urgent?"},
                "team": {
                    "type": "choice",
                    "instructions": "Route?",
                    "criteria": {"billing": "Payment issues", "support": "Technical issues"},
                },
                "severity": {
                    "type": "score",
                    "instructions": "Severity?",
                    "criteria": ["low", "high"],
                },
            },
        }
        rows, mappings = request_rows(payload)
        self.assertEqual([row["id"] for row in rows], ["urgent", "team", "severity"])
        results = [
            {"probabilities": [0.2, 0.8]},
            {"probabilities": [0.7, 0.3]},
            {"probabilities": [0.25, 0.75]},
        ]
        answers = response_answers(results, mappings)
        self.assertEqual(answers["urgent"]["noul"], 0.8)
        self.assertEqual(answers["team"]["choice"], "billing")
        self.assertEqual(answers["severity"]["score"], 0.75)

    def test_rejects_invalid_choice(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least two"):
            request_rows({
                "state": "x",
                "questions": {"q": {"type": "choice", "instructions": "x", "criteria": {"only": "one"}}},
            })


if __name__ == "__main__":
    unittest.main()
