#!/usr/bin/env python3
"""Compare architecture options without allowing scores to override hard constraints.

Usage: python3 scripts/evaluate_options.py assets/option-matrix.example.json

Input schema (all displayed fields are required; additional fields are rejected):
  {"schema_version": 1,
   "criteria": [{"id": "changeability", "description": "Scope of a typical change",
                 "weight": 2}],
   "constraints": [{"id": "budget", "description": "Agreed operating-cost limit"}],
   "options": [{"id": "option-a",
                "scores": {"changeability": {"score": 4, "evidence": "Rationale"}},
                "constraints": {"budget": {"status": "unknown", "evidence": "No quote"}},
                "assumptions": ["Traffic estimate remains unverified"]}]}

IDs must be unique nonempty strings within each list. Scores are finite numbers in
[0, 5]; weights are finite and positive. Booleans are not numbers. A constraint
status is pass, fail, or unknown. Every criterion and constraint needs exactly one
entry per option, including nonempty evidence. Empty constraints and assumptions
lists are permitted when explicitly supplied. Evidence is recorded, not verified.

Only options with every constraint marked pass are ranked. Any fail makes an
option infeasible; otherwise any unknown makes it provisional. Weighted scores
are conditional judgments, not probabilities, performance results, or proof.
Scores are not rounded before ranking. Scores within 1e-9 of a group's highest
score share a competition rank; group ties are explicit and do not depend on
input order. Change weights and rerun to explore preference sensitivity.

The script reads one local JSON file, writes JSON to stdout, and performs no
network calls or file writes. Exit status: 0 valid report; 2 invalid input.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path


TIE_TOLERANCE = 1e-9


class ValidationError(ValueError):
    """An input does not conform to the decision schema."""


def _object(value, keys, path):
    if not isinstance(value, dict):
        raise ValidationError(f"{path} must be an object")
    missing = set(keys) - value.keys()
    extra = value.keys() - set(keys)
    if missing or extra:
        raise ValidationError(
            f"{path}: missing fields {sorted(missing)}; unexpected fields {sorted(extra)}"
        )


def _text(value, path):
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{path} must be a nonempty string")
    if value != value.strip():
        raise ValidationError(f"{path} must not have surrounding whitespace")


def _number(value, path, *, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(f"{path} must be a finite number, not a boolean")
    try:
        result = float(value)
    except OverflowError as exc:
        raise ValidationError(f"{path} is outside the supported numeric range") from exc
    if not math.isfinite(result) or (positive and result <= 0):
        raise ValidationError(f"{path} must be finite{' and positive' if positive else ''}")
    return result


def _records(value, keys, path, *, nonempty=False):
    if not isinstance(value, list) or (nonempty and not value):
        raise ValidationError(f"{path} must be a{' nonempty' if nonempty else ''} list")
    seen = set()
    for index, record in enumerate(value):
        at = f"{path}[{index}]"
        _object(record, keys, at)
        _text(record["id"], f"{at}.id")
        if record["id"] in seen:
            raise ValidationError(f"{path} contains duplicate ID {record['id']!r}")
        seen.add(record["id"])
    return seen


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError(f"Duplicate JSON key {key!r}")
        result[key] = value
    return result


def _reject_constant(value):
    raise ValidationError(f"Nonstandard JSON number {value!r} is not allowed")


def load_document(text):
    """Parse JSON without silently dropping duplicate keys or accepting NaN."""
    return json.loads(
        text, object_pairs_hook=_unique_object, parse_constant=_reject_constant
    )


def evaluate(document):
    """Validate a decision and return a reproducible conditional ranking."""
    _object(document, {"schema_version", "criteria", "constraints", "options"}, "input")
    if type(document["schema_version"]) is not int or document["schema_version"] != 1:
        raise ValidationError("schema_version must be the integer 1")
    criteria = document["criteria"]
    constraints = document["constraints"]
    options = document["options"]
    criterion_ids = _records(criteria, {"id", "description", "weight"}, "criteria", nonempty=True)
    constraint_ids = _records(constraints, {"id", "description"}, "constraints")
    _records(options, {"id", "scores", "constraints", "assumptions"}, "options", nonempty=True)

    weights = []
    for criterion in criteria:
        _text(criterion["description"], f"criteria.{criterion['id']}.description")
        weights.append(_number(criterion["weight"], f"criteria.{criterion['id']}.weight", positive=True))
    for constraint in constraints:
        _text(constraint["description"], f"constraints.{constraint['id']}.description")
    # Scaling avoids overflow when individually valid, large weights are summed.
    largest = max(weights)
    normalized = [weight / largest for weight in weights]
    if any(weight == 0 for weight in normalized):
        raise ValidationError("Weight ratios are too extreme for reliable floating-point evaluation")
    weight_total = math.fsum(normalized)

    results = []
    for option in options:
        at = f"options.{option['id']}"
        _object(option["scores"], criterion_ids, f"{at}.scores")
        _object(option["constraints"], constraint_ids, f"{at}.constraints")
        if not isinstance(option["assumptions"], list):
            raise ValidationError(f"{at}.assumptions must be an explicit list")
        for index, assumption in enumerate(option["assumptions"]):
            _text(assumption, f"{at}.assumptions[{index}]")
        weighted = []
        for criterion, weight in zip(criteria, normalized):
            assessment = option["scores"][criterion["id"]]
            where = f"{at}.scores.{criterion['id']}"
            _object(assessment, {"score", "evidence"}, where)
            score = _number(assessment["score"], f"{where}.score")
            if not 0 <= score <= 5:
                raise ValidationError(f"{where}.score must be between 0 and 5 inclusive")
            _text(assessment["evidence"], f"{where}.evidence")
            weighted.append(score * weight)
        failed, unknown = [], []
        for constraint in constraints:
            key = constraint["id"]
            assessment = option["constraints"][key]
            where = f"{at}.constraints.{key}"
            _object(assessment, {"status", "evidence"}, where)
            status = assessment["status"]
            if not isinstance(status, str) or status not in {"pass", "fail", "unknown"}:
                raise ValidationError(f"{where}.status must be pass, fail, or unknown")
            _text(assessment["evidence"], f"{where}.evidence")
            if status == "fail":
                failed.append(key)
            elif status == "unknown":
                unknown.append(key)
        results.append({
            "id": option["id"],
            "eligibility": "infeasible" if failed else "provisional" if unknown else "eligible",
            "weighted_score": math.fsum(weighted) / weight_total,
            "rank": None,
            "failed_constraints": failed,
            "unknown_constraints": unknown,
            "scores": option["scores"],
            "constraints": option["constraints"],
            "assumptions": option["assumptions"],
        })

    eligible = sorted(
        (result for result in results if result["eligibility"] == "eligible"),
        key=lambda result: (-result["weighted_score"], result["id"]),
    )
    ranking = []
    for index, result in enumerate(eligible):
        if not ranking or not math.isclose(
            result["weighted_score"], ranking[-1]["highest_score"], rel_tol=0,
            abs_tol=TIE_TOLERANCE,
        ):
            ranking.append({
                "rank": index + 1, "option_ids": [], "tied": False,
                "highest_score": result["weighted_score"],
            })
        group = ranking[-1]
        group["option_ids"].append(result["id"])
        group["tied"] = len(group["option_ids"]) > 1
        result["rank"] = group["rank"]

    return {
        "schema_version": 1,
        "method": {
            "score_range": [0, 5],
            "aggregation": "Weighted arithmetic mean; only hard-constraint passes are ranked",
            "tie_absolute_tolerance": TIE_TOLERANCE,
            "caveat": (
                "Evidence and constraint coverage are not verified. Scores and weights are "
                "judgments, not measurements or proof. A high score cannot override a failed "
                "or unknown constraint. Vary plausible weights and assumptions before deciding."
            ),
        },
        "criteria": criteria,
        "constraints": constraints,
        "ranking": ranking,
        "options": results,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input", type=Path, help="Local JSON decision file")
    args = parser.parse_args(argv)
    try:
        document = load_document(args.input.read_text(encoding="utf-8"))
        report = evaluate(document)
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        print(f"Invalid decision input: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, ensure_ascii=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
