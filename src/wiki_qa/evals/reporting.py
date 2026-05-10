"""Summary table and JSON output for eval results."""
from __future__ import annotations

import json
import os

from wiki_qa.evals.runner import CaseResult

_GRADERS = ["fact_recall", "search_behavior", "honest_failure", "faithfulness"]
_SHORT = {"fact_recall": "fact", "search_behavior": "search", "honest_failure": "honest", "faithfulness": "faith"}

_PASS = "✓"
_FAIL = "✗"
_NA   = "·"
_SKIP = "−"


def _sym(grade: dict | None) -> str:
    if grade is None:
        return _SKIP
    if not grade.get("applicable", True):
        return _NA
    return _PASS if grade["passed"] else _FAIL


def _score(cases: list[CaseResult], grader: str) -> str:
    applicable = [r for r in cases if r.grades.get(grader) is not None and r.grades[grader].get("applicable", True)]
    if not applicable:
        return "n/a"
    passed = sum(1 for r in applicable if r.grades[grader]["passed"])
    return f"{passed}/{len(applicable)}"


def summarize(results: list[CaseResult]) -> None:
    """Print symbol-based summary, per-case table grouped by category, and pass rates."""
    # Graders that were actually run in this batch
    run_graders = [g for g in _GRADERS if any(g in r.grades for r in results)]

    # Category groups preserving dataset order
    cats: dict[str, list[CaseResult]] = {}
    for r in results:
        cats.setdefault(r.case.category, []).append(r)

    n_cases = len(results)
    n_graders = len(run_graders)
    print(f"\nWikipedia QA eval suite — {n_cases} cases, {n_graders} graders\n")

    # Summary bar: one row per grader, symbols grouped by category
    for g in run_graders:
        cat_blocks = ["".join(_sym(r.grades.get(g)) for r in cat_rs) for cat_rs in cats.values()]
        sym_str = "  ".join(cat_blocks)
        score = _score(results, g)
        label = _SHORT.get(g, g)
        print(f"  {label:<10} {sym_str}   {score}")

    # Per-case table grouped by category
    print("\nBy case:\n")
    for cat, cat_results in cats.items():
        print(f"{cat} ({len(cat_results)})")
        for r in cat_results:
            row_syms = "".join(_sym(r.grades.get(g)) for g in run_graders)
            detail = "  ".join(
                f"{_SHORT.get(g, g)}:{_sym(r.grades.get(g))}" for g in run_graders
            )
            print(f"  {row_syms}  {r.case.id:<42} {detail}")
        print()

    # Per-category pass rates
    print("Per-category pass rates:")
    for cat, cat_results in cats.items():
        parts = []
        for g in run_graders:
            applicable = [r for r in cat_results if r.grades.get(g) is not None and r.grades[g].get("applicable", True)]
            if not applicable:
                parts.append(f"{_SHORT.get(g, g)}:n/a")
            else:
                passed = sum(1 for r in applicable if r.grades[g]["passed"])
                parts.append(f"{_SHORT.get(g, g)}:{passed}/{len(applicable)}")
        print(f"  {cat:<30} {', '.join(parts)}")

    # Overall
    print()
    print("Overall:")
    for g in run_graders:
        applicable = [r for r in results if r.grades.get(g) is not None and r.grades[g].get("applicable", True)]
        if applicable:
            passed = sum(1 for r in applicable if r.grades[g]["passed"])
            pct = 100 * passed // len(applicable)
            print(f"  {g}: {passed}/{len(applicable)} ({pct}%)")
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
            ] if r.answer_result.retrieved else [],
            "grades": r.grades,
        })
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"\nResults written to {path}")
