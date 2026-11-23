"""Behavioral tests for hard constraints, input integrity, and deterministic ranking."""

import copy
import importlib.util
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SKILL_DIR = Path(os.environ.get(
    "TECHNICAL_ARCHITECT_SKILL_DIR",
    str(Path(__file__).resolve().parents[1] / "technical-architect"),
))
SCRIPT = SKILL_DIR / "scripts" / "evaluate_options.py"
SPEC = importlib.util.spec_from_file_location("evaluate_options", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def fixture():
    return {
        "schema_version": 1,
        "criteria": [
            {"id": "simplicity", "description": "Implementation complexity", "weight": 3},
            {"id": "scaling", "description": "Workload isolation", "weight": 1},
        ],
        "constraints": [{"id": "budget", "description": "Agreed cost ceiling"}],
        "options": [{
            "id": "a",
            "scores": {
                "simplicity": {"score": 4, "evidence": "Hypothetical team assessment"},
                "scaling": {"score": 2, "evidence": "Hypothetical team assessment"},
            },
            "constraints": {"budget": {"status": "pass", "evidence": "Hypothetical estimate"}},
            "assumptions": [],
        }],
    }


class DecisionTests(unittest.TestCase):
    def assert_invalid(self, document):
        with self.assertRaises(MODULE.ValidationError):
            MODULE.evaluate(document)

    def test_weighted_mean(self):
        result = MODULE.evaluate(fixture())
        self.assertAlmostEqual(result["options"][0]["weighted_score"], 3.5, places=12)
        self.assertEqual(result["options"][0]["rank"], 1)

    def test_hard_constraints_cannot_be_outvoted(self):
        document = fixture()
        for name, status in [("high-but-failed", "fail"), ("high-but-unknown", "unknown")]:
            option = copy.deepcopy(document["options"][0])
            option["id"] = name
            for score in option["scores"].values():
                score["score"] = 5
            option["constraints"]["budget"]["status"] = status
            document["options"].append(option)
        result = MODULE.evaluate(document)
        self.assertEqual(result["ranking"][0]["option_ids"], ["a"])
        self.assertEqual([option["eligibility"] for option in result["options"]],
                         ["eligible", "infeasible", "provisional"])
        self.assertEqual([option["rank"] for option in result["options"]], [1, None, None])

    def test_failed_takes_precedence_over_unknown(self):
        document = fixture()
        document["constraints"].append({"id": "residency", "description": "Required region"})
        document["options"][0]["constraints"]["budget"]["status"] = "fail"
        document["options"][0]["constraints"]["residency"] = {"status": "unknown", "evidence": "Unverified"}
        result = MODULE.evaluate(document)
        self.assertEqual(result["options"][0]["eligibility"], "infeasible")
        self.assertEqual(result["options"][0]["unknown_constraints"], ["residency"])
        self.assertEqual(result["ranking"], [])

    def test_missing_and_extra_assessments(self):
        for field, key in [("scores", "simplicity"), ("constraints", "budget")]:
            with self.subTest(field=field, missing=True):
                document = fixture()
                del document["options"][0][field][key]
                self.assert_invalid(document)
            with self.subTest(field=field, extra=True):
                document = fixture()
                document["options"][0][field]["unexpected"] = {}
                self.assert_invalid(document)

    def test_evidence_required(self):
        for field, key in [("scores", "simplicity"), ("constraints", "budget")]:
            for value in ["", "  ", None, 42]:
                with self.subTest(field=field, value=value):
                    document = fixture()
                    document["options"][0][field][key]["evidence"] = value
                    self.assert_invalid(document)

    def test_duplicate_ids(self):
        for key in ["criteria", "constraints", "options"]:
            with self.subTest(key=key):
                document = fixture()
                document[key].append(copy.deepcopy(document[key][0]))
                self.assert_invalid(document)

    def test_invalid_weights(self):
        for value in [True, False, 0, -1, math.nan, math.inf, "1", 10 ** 400]:
            with self.subTest(value=str(value)[:20]):
                document = fixture()
                document["criteria"][0]["weight"] = value
                self.assert_invalid(document)

    def test_invalid_scores(self):
        for value in [-0.001, 5.001, True, math.nan, math.inf, "4", None]:
            with self.subTest(value=value):
                document = fixture()
                document["options"][0]["scores"]["simplicity"]["score"] = value
                self.assert_invalid(document)

    def test_nonstandard_json_and_duplicate_keys(self):
        for text in ['{"value": NaN}', '{"value": Infinity}', '{"value": -Infinity}',
                     '{"key": 1, "key": 2}', '{"nested": {"key": 1, "key": 2}}']:
            with self.subTest(text=text):
                with self.assertRaises(MODULE.ValidationError):
                    MODULE.load_document(text)

    def test_finite_weights_do_not_overflow(self):
        document = fixture()
        document["criteria"][0]["weight"] = 1e308
        document["criteria"][1]["weight"] = 1e308
        result = MODULE.evaluate(document)
        self.assertEqual(result["options"][0]["weighted_score"], 3)

    def test_unrepresentable_weight_ratios_rejected(self):
        document = fixture()
        document["criteria"][0]["weight"] = 1e308
        document["criteria"][1]["weight"] = 1e-308
        self.assert_invalid(document)

    def test_explicit_ties_and_stable_ranking(self):
        document = fixture()
        for name, score in [("b", 4 + 0.5e-9), ("c", 3)]:
            option = copy.deepcopy(document["options"][0])
            option["id"] = name
            option["scores"]["simplicity"]["score"] = score
            document["options"].append(option)
        result = MODULE.evaluate(document)
        self.assertTrue(result["ranking"][0]["tied"])
        self.assertEqual(set(result["ranking"][0]["option_ids"]), {"a", "b"})
        self.assertEqual(result["ranking"][1]["rank"], 3)
        document["options"].reverse()
        self.assertEqual(MODULE.evaluate(document)["ranking"], result["ranking"])

    def test_close_scores_not_rounded_into_a_tie(self):
        document = fixture()
        other = copy.deepcopy(document["options"][0])
        other["id"] = "b"
        other["scores"]["simplicity"]["score"] += 0.000001
        document["options"].append(other)
        result = MODULE.evaluate(document)
        self.assertEqual(result["ranking"][0]["option_ids"], ["b"])
        self.assertEqual(result["ranking"][1]["option_ids"], ["a"])

    def test_explicit_empty_constraints(self):
        document = fixture()
        document["constraints"] = []
        document["options"][0]["constraints"] = {}
        self.assertEqual(MODULE.evaluate(document)["options"][0]["eligibility"], "eligible")

    def test_explicit_assumptions_and_version(self):
        for value in [None, "unknown", [""], [False]]:
            document = fixture()
            document["options"][0]["assumptions"] = value
            self.assert_invalid(document)
        document = fixture()
        del document["options"][0]["assumptions"]
        self.assert_invalid(document)
        for value in [True, 1.0, "1", 2]:
            document = fixture()
            document["schema_version"] = value
            self.assert_invalid(document)

    def test_cli_exit_codes_and_no_output_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            path.write_text(json.dumps(fixture()), encoding="utf-8")
            good = subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True)
            self.assertEqual(good.returncode, 0, good.stderr)
            self.assertAlmostEqual(json.loads(good.stdout)["options"][0]["weighted_score"], 3.5, places=12)
            path.write_text('{"schema_version": 1, "schema_version": 2}', encoding="utf-8")
            bad = subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True)
            self.assertEqual(bad.returncode, 2)
            self.assertEqual(bad.stdout, "")
            self.assertIn("Duplicate JSON key", bad.stderr)
            self.assertEqual(list(Path(directory).iterdir()), [path])

    def test_committed_example_is_valid_and_hypothetical(self):
        text = (SKILL_DIR / "assets" / "option-matrix.example.json").read_text(encoding="utf-8")
        result = MODULE.evaluate(MODULE.load_document(text))
        self.assertEqual(result["ranking"][0]["option_ids"], ["modular-monolith"])
        self.assertEqual(result["options"][1]["eligibility"], "provisional")
        self.assertIn("hypothetical", text.lower())


if __name__ == "__main__":
    unittest.main()
