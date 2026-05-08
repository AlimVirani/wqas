"""Grader functions for eval cases."""
from __future__ import annotations

from wiki_qa.agent import AnswerResult
from wiki_qa.evals.dataset import EvalCase


def fact_recall(case: EvalCase, result: AnswerResult) -> dict:
    """Returns {'passed': bool, 'matched': list[str], 'missing': list[str]}."""
    answer_lower = result.answer.lower()
    matched = [f for f in case.expected_facts if f.lower() in answer_lower]
    missing = [f for f in case.expected_facts if f.lower() not in answer_lower]
    return {"passed": len(missing) == 0, "matched": matched, "missing": missing}
