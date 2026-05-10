"""Runs eval cases through the agent and collects results."""
from __future__ import annotations

from dataclasses import dataclass

from wiki_qa import agent
from wiki_qa.agent import AnswerResult
from wiki_qa.evals.dataset import EvalCase
from wiki_qa.evals.graders import fact_recall, faithfulness, honest_failure, search_behavior


@dataclass
class CaseResult:
    case: EvalCase
    answer_result: AnswerResult
    grades: dict[str, dict]


def _grade_label(grade: dict) -> str:
    if not grade.get("applicable", True):
        return "n/a"
    return "PASS" if grade["passed"] else "FAIL"


def run_cases(
    cases: list[EvalCase],
    *,
    run_automated: bool = True,
    run_judges: bool = True,
) -> list[CaseResult]:
    """Run each case through the agent and grade it."""
    results: list[CaseResult] = []
    for case in cases:
        print(f"running: {case.id}")
        try:
            answer_result = agent.answer(case.question)
        except agent.MaxTurnsExceeded as e:
            print(f"  WARN: max turns exceeded, using partial result")
            answer_result = e.partial
        except Exception as e:
            print(f"  ERROR: {e}")
            answer_result = AnswerResult(answer=f"[agent error: {e}]", searches=[], retrieved=[], messages=[])
        grades: dict[str, dict] = {}
        if run_automated:
            grades["fact_recall"] = fact_recall(case, answer_result)
            grades["search_behavior"] = search_behavior(case, answer_result)
        if run_judges:
            grades["honest_failure"] = honest_failure(case, answer_result)
            grades["faithfulness"] = faithfulness(case, answer_result)
        parts = "  ".join(
            f"{k}: {_grade_label(v)}" for k, v in grades.items()
        )
        print(f"  {parts}")
        results.append(CaseResult(case=case, answer_result=answer_result, grades=grades))
    return results
