from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from jevbench.backends import HttpSystemOneBackend, OracleBackend, ReplayBackend, backend_from_config
from jevbench.corpus import build_corpus
from jevbench.validation import normalize_prediction


class BackendTests(unittest.TestCase):
    def test_http_endpoint_is_normalized(self):
        self.assertEqual(HttpSystemOneBackend("http://example.test").url, "http://example.test/v1/systemone")
        self.assertEqual(
            HttpSystemOneBackend("http://example.test/v1/systemone").url,
            "http://example.test/v1/systemone",
        )

    def test_oracle_uses_valid_wire_shape(self):
        case = build_corpus()[0]
        normalized = normalize_prediction(case, OracleBackend().predict(case, "oracle"))
        self.assertEqual(set(normalized), set(case.questions))

    def test_replay_round_trip(self):
        case = build_corpus()[0]
        response = OracleBackend().predict(case, "oracle").raw
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "replay.jsonl"
            path.write_text(
                json.dumps({"case_id": case.id, "latency_ms": 12.5, "response": response}) + "\n",
                encoding="utf-8",
            )
            prediction = ReplayBackend(path).predict(case, "replay")
        self.assertEqual(prediction.latency_ms, 12.5)
        self.assertIsNone(prediction.error)

    def test_missing_replay_case_is_an_error(self):
        case = build_corpus()[0]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "replay.jsonl"
            path.write_text("", encoding="utf-8")
            prediction = ReplayBackend(path).predict(case, "replay")
        self.assertIsNotNone(prediction.error)

    def test_backend_factory_rejects_missing_configuration(self):
        with self.assertRaises(ValueError):
            backend_from_config("command")


if __name__ == "__main__":
    unittest.main()

