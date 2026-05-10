"""Tests for wiki_qa.evals.graders — Anthropic client is mocked."""
from types import SimpleNamespace
from unittest.mock import MagicMock

from wiki_qa.agent import AnswerResult
from wiki_qa.evals.dataset import EvalCase
from wiki_qa.evals.graders import honest_failure


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _case(*, expected_abstention: bool) -> EvalCase:
    return EvalCase(
        id="test_case",
        question="What university did X attend?",
        category="lead_section_insufficient",
        expected_abstention=expected_abstention,
    )


def _result(answer: str = "Some answer.") -> AnswerResult:
    return AnswerResult(answer=answer, searches=["query one"], messages=[])


def _make_client(json_text: str) -> MagicMock:
    block = SimpleNamespace(text=json_text)
    response = MagicMock()
    response.content = [block]
    client = MagicMock()
    client.messages.create.return_value = response
    return client


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_non_abstention_case_returns_not_applicable() -> None:
    client = MagicMock()
    grade = honest_failure(_case(expected_abstention=False), _result(), client=client)
    assert grade == {"applicable": False}
    client.messages.create.assert_not_called()


def test_abstention_case_valid_json_passing_verdict() -> None:
    payload = '{"verdict": "appropriate_abstention", "rationale": "Clearly stated it could not find the answer."}'
    client = _make_client(payload)
    grade = honest_failure(_case(expected_abstention=True), _result(), client=client)
    assert grade["applicable"] is True
    assert grade["passed"] is True
    assert grade["verdict"] == "appropriate_abstention"
    assert "rationale" in grade
    client.messages.create.assert_called_once()


def test_abstention_case_valid_json_failing_verdict() -> None:
    payload = '{"verdict": "over_claimed", "rationale": "Answer was confident despite thin evidence."}'
    client = _make_client(payload)
    grade = honest_failure(_case(expected_abstention=True), _result(), client=client)
    assert grade["applicable"] is True
    assert grade["passed"] is False
    assert grade["verdict"] == "over_claimed"


def test_abstention_case_json_in_markdown_fences() -> None:
    payload = '```json\n{"verdict": "appropriate_hedging", "rationale": "Explicitly noted extract limitations."}\n```'
    client = _make_client(payload)
    grade = honest_failure(_case(expected_abstention=True), _result(), client=client)
    assert grade["applicable"] is True
    assert grade["passed"] is True
    assert grade["verdict"] == "appropriate_hedging"


def test_abstention_case_malformed_json_returns_judge_error() -> None:
    client = _make_client("not valid json at all")
    grade = honest_failure(_case(expected_abstention=True), _result(), client=client)
    assert grade["applicable"] is True
    assert grade["passed"] is False
    assert grade["verdict"] == "judge_error"
    assert "rationale" in grade
