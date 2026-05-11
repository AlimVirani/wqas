"""Unit tests for automated graders — no mocking needed, pure functions."""
from wiki_qa.agent import AnswerResult
from wiki_qa.evals.dataset import EvalCase
from wiki_qa.evals.graders.automated import fact_recall, search_behavior


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _case(
    *,
    expected_facts: list[str] | None = None,
    expected_abstention: bool = False,
    min_searches: int = 1,
    max_searches: int | None = None,
) -> EvalCase:
    return EvalCase(
        id="test",
        question="Q?",
        category="simple_factual",
        expected_facts=expected_facts or [],
        expected_abstention=expected_abstention,
        min_searches=min_searches,
        max_searches=max_searches,
    )


def _result(answer: str = "", searches: list[str] | None = None) -> AnswerResult:
    return AnswerResult(
        answer=answer,
        searches=searches or [],
        retrieved=[],
        messages=[],
    )


# ---------------------------------------------------------------------------
# fact_recall
# ---------------------------------------------------------------------------

def test_fact_recall_abstention_case_not_applicable() -> None:
    grade = fact_recall(_case(expected_abstention=True), _result("some answer"))
    assert grade == {"applicable": False}


def test_fact_recall_all_facts_present_passes() -> None:
    grade = fact_recall(
        _case(expected_facts=["Paris", "France"]),
        _result("Paris is the capital of France."),
    )
    assert grade["applicable"] is True
    assert grade["passed"] is True
    assert grade["missing"] == []
    assert set(grade["matched"]) == {"Paris", "France"}


def test_fact_recall_missing_fact_fails() -> None:
    grade = fact_recall(
        _case(expected_facts=["Paris", "Eiffel Tower"]),
        _result("Paris is a city."),
    )
    assert grade["passed"] is False
    assert grade["missing"] == ["Eiffel Tower"]
    assert grade["matched"] == ["Paris"]


def test_fact_recall_case_insensitive() -> None:
    grade = fact_recall(
        _case(expected_facts=["CANBERRA"]),
        _result("The capital is canberra."),
    )
    assert grade["passed"] is True


def test_fact_recall_empty_expected_facts_passes() -> None:
    grade = fact_recall(_case(expected_facts=[]), _result("anything"))
    assert grade["applicable"] is True
    assert grade["passed"] is True
    assert grade["missing"] == []


def test_fact_recall_unicode_subscript_matches_ascii() -> None:
    grade = fact_recall(
        _case(expected_facts=["H2O"]),
        _result("The chemical formula is H₂O."),
    )
    assert grade["passed"] is True


# ---------------------------------------------------------------------------
# search_behavior
# ---------------------------------------------------------------------------

def test_search_behavior_within_bounds_passes() -> None:
    grade = search_behavior(
        _case(min_searches=1, max_searches=3),
        _result(searches=["q1", "q2"]),
    )
    assert grade["passed"] is True
    assert grade["actual"] == 2


def test_search_behavior_below_min_fails() -> None:
    grade = search_behavior(
        _case(min_searches=2),
        _result(searches=["q1"]),
    )
    assert grade["passed"] is False
    assert grade["actual"] == 1
    assert grade["expected_min"] == 2


def test_search_behavior_above_max_fails() -> None:
    grade = search_behavior(
        _case(min_searches=1, max_searches=2),
        _result(searches=["q1", "q2", "q3"]),
    )
    assert grade["passed"] is False
    assert grade["actual"] == 3
    assert grade["expected_max"] == 2


def test_search_behavior_no_max_passes_any_count() -> None:
    grade = search_behavior(
        _case(min_searches=1, max_searches=None),
        _result(searches=["q1", "q2", "q3", "q4", "q5"]),
    )
    assert grade["passed"] is True
    assert grade["expected_max"] is None


def test_search_behavior_returns_query_list() -> None:
    queries = ["Treaty of Westphalia", "Thirty Years War"]
    grade = search_behavior(_case(), _result(searches=queries))
    assert grade["queries"] == queries
