"""Reporting utilities for eval results."""
from __future__ import annotations

import json
import os

from wiki_qa.evals.runner import CaseResult


def summarize(results: list[CaseResult]) -> None:
    """Print a summary table and overall pass rate."""
    print()
    print(f"{'id':<30} {'category':<20} {'passed'}")
    print("-" * 60)
    passed_count = 0
    for r in results:
        passed = r.grades["fact_recall"]["passed"]
        if passed:
            passed_count += 1
        mark = "PASS" if passed else "FAIL"
        print(f"{r.case.id:<30} {r.case.category:<20} {mark}")
    print("-" * 60)
    total = len(results)
    print(f"Pass rate: {passed_count}/{total} ({100 * passed_count // total if total else 0}%)")


def dump_json(results: list[CaseResult], path: str) -> None:
    """Write full result data as JSON to path."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    payload = []
    for r in results:
        payload.append({
            "id": r.case.id,
            "question": r.case.question,
            "category": r.case.category,
            "expected_facts": r.case.expected_facts,
            "answer": r.answer_result.answer,
            "searches": r.answer_result.searches,
            "grades": r.grades,
        })
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"\nResults written to {path}")
