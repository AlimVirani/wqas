"""Tests for wiki_qa.wikipedia — all HTTP calls are mocked."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from wiki_qa.wikipedia import SearchResult, search


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_response(pages: dict | None) -> MagicMock:
    """Build a fake requests.Response that returns the given pages dict."""
    mock = MagicMock()
    mock.raise_for_status.return_value = None
    if pages is None:
        mock.json.return_value = {}
    else:
        mock.json.return_value = {"query": {"pages": pages}}
    return mock


# ---------------------------------------------------------------------------
# SearchResult dataclass
# ---------------------------------------------------------------------------

def test_search_result_fields() -> None:
    r = SearchResult(title="Jane Austen", extract="English novelist.")
    assert r.title == "Jane Austen"
    assert r.extract == "English novelist."


def test_search_result_is_dataclass() -> None:
    """SearchResult must support equality comparison (dataclass default)."""
    a = SearchResult(title="X", extract="Y")
    b = SearchResult(title="X", extract="Y")
    assert a == b


# ---------------------------------------------------------------------------
# search() — happy path
# ---------------------------------------------------------------------------

def test_search_single_result() -> None:
    pages = {"123": {"title": "Jane Austen", "extract": "Jane Austen was an English novelist."}}
    with patch("wiki_qa.wikipedia.requests.get", return_value=_mock_response(pages)):
        results = search("Jane Austen")
    assert len(results) == 1
    assert results[0].title == "Jane Austen"
    assert results[0].extract == "Jane Austen was an English novelist."


def test_search_multiple_results() -> None:
    pages = {
        "1": {"title": "Alpha", "extract": "Extract A"},
        "2": {"title": "Beta", "extract": "Extract B"},
    }
    with patch("wiki_qa.wikipedia.requests.get", return_value=_mock_response(pages)):
        results = search("query")
    assert len(results) == 2
    assert {r.title for r in results} == {"Alpha", "Beta"}


def test_search_result_order_by_index() -> None:
    """Results must be sorted by the MediaWiki 'index' field, not dict insertion order."""
    pages = {
        "20": {"title": "Second", "extract": "Extract B", "index": 2},
        "10": {"title": "First", "extract": "Extract A", "index": 1},
    }
    with patch("wiki_qa.wikipedia.requests.get", return_value=_mock_response(pages)):
        results = search("query")
    assert [r.title for r in results] == ["First", "Second"]


def test_search_returns_list_of_search_results() -> None:
    pages = {"9": {"title": "T", "extract": "E"}}
    with patch("wiki_qa.wikipedia.requests.get", return_value=_mock_response(pages)):
        results = search("anything")
    assert isinstance(results, list)
    assert all(isinstance(r, SearchResult) for r in results)


# ---------------------------------------------------------------------------
# search() — edge / error cases
# ---------------------------------------------------------------------------

def test_search_empty_pages_dict() -> None:
    """API returns a query key but no pages — should return empty list."""
    mock = MagicMock()
    mock.raise_for_status.return_value = None
    mock.json.return_value = {"query": {"pages": {}}}
    with patch("wiki_qa.wikipedia.requests.get", return_value=mock):
        results = search("xyzzy nonexistent query")
    assert results == []


def test_search_no_query_key() -> None:
    """API returns empty body (e.g. no results) — should return empty list."""
    with patch("wiki_qa.wikipedia.requests.get", return_value=_mock_response(None)):
        results = search("xyzzy nonexistent query")
    assert results == []


def test_search_page_missing_extract() -> None:
    """A page with no 'extract' key should produce extract=''."""
    pages = {"42": {"title": "No Extract Page"}}
    with patch("wiki_qa.wikipedia.requests.get", return_value=_mock_response(pages)):
        results = search("something")
    assert len(results) == 1
    assert results[0].title == "No Extract Page"
    assert results[0].extract == ""


def test_search_page_empty_extract() -> None:
    """A page with extract='' is preserved as-is."""
    pages = {"7": {"title": "Stub", "extract": ""}}
    with patch("wiki_qa.wikipedia.requests.get", return_value=_mock_response(pages)):
        results = search("stub article")
    assert results[0].extract == ""


def test_search_raises_on_http_error() -> None:
    """HTTP errors from raise_for_status() must propagate."""
    mock = MagicMock()
    mock.raise_for_status.side_effect = Exception("503 Service Unavailable")
    with patch("wiki_qa.wikipedia.requests.get", return_value=mock):
        with pytest.raises(Exception, match="503"):
            search("test")


# ---------------------------------------------------------------------------
# search() — API call contract
# ---------------------------------------------------------------------------

def test_search_passes_query_param() -> None:
    """The user's query string must reach the API as the search parameter."""
    pages = {}
    with patch("wiki_qa.wikipedia.requests.get", return_value=_mock_response(pages)) as mock_get:
        search("python programming language")
    params = mock_get.call_args.kwargs.get("params") or mock_get.call_args.args[1]
    assert "python programming language" in params.values()


def test_search_calls_wikipedia_api() -> None:
    """Must call the English Wikipedia API endpoint."""
    with patch("wiki_qa.wikipedia.requests.get", return_value=_mock_response({})) as mock_get:
        search("anything")
    url = mock_get.call_args.args[0]
    assert "wikipedia.org" in url


def test_search_sends_user_agent_header() -> None:
    """Must include a non-empty User-Agent header (MediaWiki API policy)."""
    with patch("wiki_qa.wikipedia.requests.get", return_value=_mock_response({})) as mock_get:
        search("anything")
    headers = mock_get.call_args.kwargs.get("headers", {})
    assert headers.get("User-Agent")


def test_search_passes_timeout() -> None:
    """Must pass a timeout to requests.get to avoid hanging forever."""
    with patch("wiki_qa.wikipedia.requests.get", return_value=_mock_response({})) as mock_get:
        search("anything")
    timeout = mock_get.call_args.kwargs.get("timeout")
    assert timeout is not None
    assert timeout > 0
