"""Tests for wiki_qa.evals.graders — Anthropic client is mocked."""
from types import SimpleNamespace
from unittest.mock import MagicMock

from wiki_qa.agent import AnswerResult
from wiki_qa.evals.dataset import EvalCase
from wiki_qa.evals.graders import faithfulness, honest_failure
from wiki_qa.wikipedia import SearchResult


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
    return AnswerResult(answer=answer, searches=["query one"], retrieved=[], messages=[])


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


# ---------------------------------------------------------------------------
# faithfulness grader
# ---------------------------------------------------------------------------

def _faithfulness_case() -> EvalCase:
    return EvalCase(
        id="faith_test",
        question="What is the capital of France?",
        category="simple_factual",
        expected_facts=["Paris"],
    )


def _result_with_retrieval(answer: str = "Paris is the capital of France.") -> AnswerResult:
    return AnswerResult(
        answer=answer,
        searches=["capital of France"],
        retrieved=[[SearchResult(title="Paris", extract="Paris is the capital of France.")]],
        messages=[],
    )


def test_faithfulness_empty_answer_not_applicable() -> None:
    result = AnswerResult(answer="", searches=[], retrieved=[], messages=[])
    grade = faithfulness(_faithfulness_case(), result, client=MagicMock())
    assert grade == {"applicable": False}


def test_faithfulness_no_retrievals_not_applicable() -> None:
    result = AnswerResult(answer="Paris.", searches=["France capital"], retrieved=[[]], messages=[])
    grade = faithfulness(_faithfulness_case(), result, client=MagicMock())
    assert grade == {"applicable": False}


def test_faithfulness_fully_supported_passes() -> None:
    payload = '{"verdict": "fully_supported", "rationale": "All claims match the extract."}'
    client = _make_client(payload)
    grade = faithfulness(_faithfulness_case(), _result_with_retrieval(), client=client)
    assert grade["applicable"] is True
    assert grade["passed"] is True
    assert grade["verdict"] == "fully_supported"
    assert "rationale" in grade


def test_faithfulness_unsupported_fails() -> None:
    payload = '{"verdict": "unsupported", "rationale": "Claim not found in any extract."}'
    client = _make_client(payload)
    grade = faithfulness(_faithfulness_case(), _result_with_retrieval(), client=client)
    assert grade["applicable"] is True
    assert grade["passed"] is False
    assert grade["verdict"] == "unsupported"


def test_faithfulness_json_in_markdown_fences() -> None:
    payload = '```json\n{"verdict": "partially_supported", "rationale": "Minor extra detail."}\n```'
    client = _make_client(payload)
    grade = faithfulness(_faithfulness_case(), _result_with_retrieval(), client=client)
    assert grade["applicable"] is True
    assert grade["passed"] is False
    assert grade["verdict"] == "partially_supported"
