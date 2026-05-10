"""Summary table and JSON output for eval results."""
from __future__ import annotations

import json
import os
from collections import defaultdict

from wiki_qa.evals.runner import CaseResult

_GRADERS = ["fact_recall", "search_behavior", "honest_failure", "faithfulness"]


def _label(grade: dict) -> str:
    if not grade.get("applicable", True):
        return "n/a"
    return "PASS" if grade["passed"] else "FAIL"


def summarize(results: list[CaseResult]) -> None:
    """Print per-case table, per-category pass rates, and overall pass rates."""
    print()
    header = f"{'id':<35} {'category':<25} {'fact_recall':<14} {'search_behavior':<18} {'honest_failure':<18} {'faithfulness'}"
    print(header)
    print("-" * len(header))
    for r in results:
        fr = _label(r.grades["fact_recall"])
        sb = _label(r.grades["search_behavior"])
        hf = _label(r.grades["honest_failure"])
        fa = _label(r.grades["faithfulness"])
        print(f"{r.case.id:<35} {r.case.category:<25} {fr:<14} {sb:<18} {hf:<18} {fa}")

    # Per-category pass rates (applicable cases only)
    cat_totals: dict[str, dict[str, list[bool]]] = defaultdict(lambda: {g: [] for g in _GRADERS})
    overall: dict[str, list[bool]] = {g: [] for g in _GRADERS}
    for r in results:
        for g in _GRADERS:
            grade = r.grades[g]
            if grade.get("applicable", True):
                cat_totals[r.case.category][g].append(grade["passed"])
                overall[g].append(grade["passed"])

    print()
    print("Per-category pass rates (applicable cases only):")
    for cat in sorted(cat_totals):
        parts = []
        for g in _GRADERS:
            vals = cat_totals[cat][g]
            if vals:
                parts.append(f"{g}: {sum(vals)}/{len(vals)}")
        print(f"  {cat}: {', '.join(parts) if parts else 'no applicable grades'}")

    print()
    print("Overall pass rates:")
    for g in _GRADERS:
        vals = overall[g]
        if vals:
            pct = 100 * sum(vals) // len(vals)
            print(f"  {g}: {sum(vals)}/{len(vals)} ({pct}%)")
        else:
            print(f"  {g}: n/a")


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
            "expected_abstention": r.case.expected_abstention,
            "min_searches": r.case.min_searches,
            "max_searches": r.case.max_searches,
            "notes": r.case.notes,
            "answer": r.answer_result.answer,
            "searches": r.answer_result.searches,
            "retrieved": [
                [{"title": sr.title, "extract": sr.extract} for sr in per_query]
                for per_query in r.answer_result.retrieved
            ],
            "grades": r.grades,
        })
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"\nResults written to {path}")
