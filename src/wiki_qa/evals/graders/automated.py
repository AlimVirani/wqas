"""Fast automated graders — no LLM calls."""
from __future__ import annotations

from wiki_qa.agent import AnswerResult
from wiki_qa.evals.dataset import EvalCase

_SUBSCRIPT_DIGITS   = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")
_SUPERSCRIPT_DIGITS = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")


def _normalize(s: str) -> str:
    return s.translate(_SUBSCRIPT_DIGITS).translate(_SUPERSCRIPT_DIGITS).lower()


def fact_recall(case: EvalCase, result: AnswerResult) -> dict:
    """Returns applicable=False for abstention cases; otherwise substring match."""
    if case.expected_abstention:
        return {"applicable": False}
    answer_norm = _normalize(result.answer)
    matched = [f for f in case.expected_facts if _normalize(f) in answer_norm]
    missing = [f for f in case.expected_facts if _normalize(f) not in answer_norm]
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
