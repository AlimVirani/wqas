"""Runs eval cases through the agent and collects results."""
from __future__ import annotations

from dataclasses import dataclass

from wiki_qa import agent
from wiki_qa.agent import AnswerResult
from wiki_qa.evals.dataset import EvalCase
from wiki_qa.evals.graders import fact_recall, honest_failure, search_behavior


@dataclass
class CaseResult:
    case: EvalCase
    answer_result: AnswerResult
    grades: dict  # grader_name -> grade dict


def _grade_label(grade: dict) -> str:
    if not grade.get("applicable", True):
        return "n/a"
    return "PASS" if grade["passed"] else "FAIL"


def run_cases(cases: list[EvalCase]) -> list[CaseResult]:
    """Run each case through the agent and grade it."""
    results: list[CaseResult] = []
    for case in cases:
        print(f"running: {case.id}")
        answer_result = agent.answer(case.question)
        grades = {
            "fact_recall": fact_recall(case, answer_result),
            "search_behavior": search_behavior(case, answer_result),
            "honest_failure": honest_failure(case, answer_result),
        }
        fr = _grade_label(grades["fact_recall"])
        sb = _grade_label(grades["search_behavior"])
        hf = _grade_label(grades["honest_failure"])
        print(f"  fact_recall: {fr}  search_behavior: {sb}  honest_failure: {hf}")
        results.append(CaseResult(case=case, answer_result=answer_result, grades=grades))
    return results
