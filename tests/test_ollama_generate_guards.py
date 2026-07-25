"""Unit tests for Ollama num_predict / stop guardrails (no live Ollama required)."""

import os
import unittest


class TestOllamaGenerateGuards(unittest.TestCase):
    def test_default_ollama_num_predict_caps_yaml(self):
        from backend.llm_providers import default_ollama_num_predict

        self.assertEqual(default_ollama_num_predict(800), 800)
        self.assertEqual(default_ollama_num_predict(None), 1200)
        self.assertEqual(default_ollama_num_predict(99999), 1200)

    def test_default_ollama_num_predict_respects_env_cap(self):
        from backend import llm_providers as lp

        old = os.environ.get("OLLAMA_NUM_PREDICT_CAP")
        try:
            os.environ["OLLAMA_NUM_PREDICT_CAP"] = "512"
            self.assertEqual(lp.default_ollama_num_predict(800), 512)
            self.assertEqual(lp.default_ollama_num_predict(None), 512)
        finally:
            if old is None:
                os.environ.pop("OLLAMA_NUM_PREDICT_CAP", None)
            else:
                os.environ["OLLAMA_NUM_PREDICT_CAP"] = old

    def test_faithh_ollama_stop_sequences(self):
        from backend.llm_providers import faithh_ollama_stop_sequences

        stops = faithh_ollama_stop_sequences()
        self.assertIn("====", stops)
        self.assertIn("[CTX:", stops)
        self.assertIn("\nUSER\n", stops)


if __name__ == "__main__":
    unittest.main()
