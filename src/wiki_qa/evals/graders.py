"""Grader functions for eval cases."""
from __future__ import annotations

from wiki_qa.agent import AnswerResult
from wiki_qa.evals.dataset import EvalCase

_ABSTENTION_PHRASES = [
    "wikipedia does not",
    "could not find",
    "couldn't find",
    "unable to find",
    "not enough information",
    "does not provide",
    "could not determine",
    "i don't have",
    "i do not have",
    "unable to determine",
]


def fact_recall(case: EvalCase, result: AnswerResult) -> dict:
    """Returns applicable=False for abstention cases; otherwise substring match."""
    if case.expected_abstention:
        return {"applicable": False}
    answer_lower = result.answer.lower()
    matched = [f for f in case.expected_facts if f.lower() in answer_lower]
    missing = [f for f in case.expected_facts if f.lower() not in answer_lower]
    return {"applicable": True, "passed": len(missing) == 0, "matched": matched, "missing": missing}


def search_behavior(case: EvalCase, result: AnswerResult) -> dict:
    """Returns whether search count falls within [min_searches, max_searches]."""
    actual = len(result.searches)
    passed = actual >= case.min_searches and (
        case.max_searches is None or actual <= case.max_searches
    )
    return {
        "passed": passed,
        "actual": actual,
        "expected_min": case.min_searches,
        "expected_max": case.max_searches,
        "queries": result.searches,
    }


def honest_failure(case: EvalCase, result: AnswerResult) -> dict:
    """Returns applicable=False for non-abstention cases; otherwise checks for hedging phrases."""
    if not case.expected_abstention:
        return {"applicable": False}
    answer_lower = result.answer.lower()
    found = [p for p in _ABSTENTION_PHRASES if p in answer_lower]
    return {"applicable": True, "passed": len(found) > 0, "abstention_phrases_found": found}
