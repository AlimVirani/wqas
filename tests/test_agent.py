"""Tests for wiki_qa.agent — Anthropic client and wikipedia.search are mocked."""
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from wiki_qa.agent import AnswerResult, answer
from wiki_qa.wikipedia import SearchResult


# ---------------------------------------------------------------------------
# Helpers to build fake Anthropic response objects
# ---------------------------------------------------------------------------

def _text_block(text: str) -> SimpleNamespace:
    return SimpleNamespace(type="text", text=text)


def _tool_use_block(tool_id: str, query: str) -> SimpleNamespace:
    return SimpleNamespace(type="tool_use", id=tool_id, input={"query": query})


def _response(stop_reason: str, *blocks) -> MagicMock:
    mock = MagicMock()
    mock.stop_reason = stop_reason
    mock.content = list(blocks)
    return mock


def _make_client(*responses) -> MagicMock:
    client = MagicMock()
    client.messages.create.side_effect = list(responses)
    return client


# ---------------------------------------------------------------------------
# Happy path: one tool call then end_turn
# ---------------------------------------------------------------------------

def test_single_search_then_answer() -> None:
    tool_response = _response("tool_use", _tool_use_block("tid1", "Marie Curie"))
    final_response = _response("end_turn", _text_block("Marie Curie discovered radium."))
    client = _make_client(tool_response, final_response)

    with patch("wiki_qa.agent.search", return_value=[
        SearchResult(title="Marie Curie", extract="Polish-French physicist."),
    ]) as mock_search:
        result = answer("Who discovered radium?", client=client)

    mock_search.assert_called_once_with("Marie Curie")
    assert result.answer == "Marie Curie discovered radium."
    assert result.searches == ["Marie Curie"]


# ---------------------------------------------------------------------------
# searches list accumulates across multiple tool calls
# ---------------------------------------------------------------------------

def test_multiple_searches_accumulated() -> None:
    r1 = _response("tool_use", _tool_use_block("t1", "Eiffel Tower"))
    r2 = _response("tool_use", _tool_use_block("t2", "Gustave Eiffel"))
    r3 = _response("end_turn", _text_block("Built by Gustave Eiffel."))
    client = _make_client(r1, r2, r3)

    with patch("wiki_qa.agent.search", return_value=[]):
        result = answer("Tell me about the Eiffel Tower.", client=client)

    assert result.searches == ["Eiffel Tower", "Gustave Eiffel"]


# ---------------------------------------------------------------------------
# tool_result block is appended with correct structure
# ---------------------------------------------------------------------------

def test_tool_result_appended_to_messages() -> None:
    tool_response = _response("tool_use", _tool_use_block("tid42", "Black hole"))
    final_response = _response("end_turn", _text_block("A black hole is a region..."))
    client = _make_client(tool_response, final_response)

    with patch("wiki_qa.agent.search", return_value=[
        SearchResult(title="Black hole", extract="Region of spacetime."),
    ]):
        result = answer("What is a black hole?", client=client)

    # messages: user, assistant (tool_use), user (tool_result), assistant (end_turn)
    tool_result_msg = result.messages[2]
    assert tool_result_msg["role"] == "user"
    blocks = tool_result_msg["content"]
    assert len(blocks) == 1
    assert blocks[0]["type"] == "tool_result"
    assert blocks[0]["tool_use_id"] == "tid42"
    assert "Black hole" in blocks[0]["content"]


# ---------------------------------------------------------------------------
# Final answer extraction
# ---------------------------------------------------------------------------

def test_answer_text_extracted_correctly() -> None:
    final_response = _response("end_turn", _text_block("The speed of light is 299,792 km/s."))
    client = _make_client(final_response)

    result = answer("Speed of light?", client=client)
    assert result.answer == "The speed of light is 299,792 km/s."


def test_messages_list_contains_full_conversation() -> None:
    tool_response = _response("tool_use", _tool_use_block("t1", "Photon"))
    final_response = _response("end_turn", _text_block("A photon is a particle of light."))
    client = _make_client(tool_response, final_response)

    with patch("wiki_qa.agent.search", return_value=[]):
        result = answer("What is a photon?", client=client)

    # user question, assistant tool_use, user tool_result, assistant end_turn
    assert len(result.messages) == 4
    assert result.messages[0] == {"role": "user", "content": "What is a photon?"}


# ---------------------------------------------------------------------------
# max_turns safety cap
# ---------------------------------------------------------------------------

def test_max_turns_raises_on_runaway() -> None:
    """A loop that never reaches end_turn must raise after max_turns."""
    runaway = _response("tool_use", _tool_use_block("t1", "query"))
    client = _make_client(*[runaway] * 5)

    with patch("wiki_qa.agent.search", return_value=[]):
        with pytest.raises(RuntimeError, match="3 turns"):
            answer("loop forever", client=client, max_turns=3)


# ---------------------------------------------------------------------------
# wikipedia.search receives the exact query from the tool_use block
# ---------------------------------------------------------------------------

def test_multiple_text_blocks_joined() -> None:
    """All text blocks in a final response must be concatenated."""
    final_response = _response("end_turn", _text_block("Part 1. "), _text_block("Part 2."))
    client = _make_client(final_response)

    result = answer("Anything?", client=client)
    assert result.answer == "Part 1. Part 2."


def test_search_called_with_exact_query() -> None:
    query = "Treaty of Westphalia"
    tool_response = _response("tool_use", _tool_use_block("t1", query))
    final_response = _response("end_turn", _text_block("Done."))
    client = _make_client(tool_response, final_response)

    with patch("wiki_qa.agent.search", return_value=[]) as mock_search:
        answer("Tell me about Westphalia.", client=client)

    mock_search.assert_called_once_with(query)
