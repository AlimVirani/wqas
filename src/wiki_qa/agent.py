"""Claude tool-use loop for Wikipedia-backed QA."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import anthropic
from dotenv import load_dotenv

from wiki_qa import config
from wiki_qa.prompts import SEARCH_WIKIPEDIA_TOOL, SYSTEM_PROMPT
from wiki_qa.wikipedia import SearchResult, search


@dataclass
class AnswerResult:
    answer: str
    searches: list[str]
    messages: list


def answer(
    question: str,
    *,
    client: anthropic.Anthropic | None = None,
    max_turns: int = 10,
    on_search: Callable[[str], None] | None = None,
) -> AnswerResult:
    """Run the tool-use loop and return the final answer plus metadata."""
    if client is None:
        load_dotenv()
        client = anthropic.Anthropic()

    messages: list = [{"role": "user", "content": question}]
    searches: list[str] = []

    for _ in range(max_turns):
        response = client.messages.create(
            model=config.MODEL,
            max_tokens=config.MAX_TOKENS,
            system=SYSTEM_PROMPT,
            tools=[SEARCH_WIKIPEDIA_TOOL],
            messages=messages,
        )

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            text = "".join(
                block.text for block in response.content if block.type == "text"
            )
            return AnswerResult(answer=text, searches=searches, messages=messages)

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                query = block.input["query"]
                if on_search is not None:
                    on_search(query)
                searches.append(query)
                results: list[SearchResult] = search(query)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": _format_results(results),
                })
            messages.append({"role": "user", "content": tool_results})

    raise RuntimeError(f"Agent did not finish within {max_turns} turns.")


def _format_results(results: list[SearchResult]) -> str:
    if not results:
        return "No results found."
    return "\n\n".join(f"**{r.title}**\n{r.extract}" for r in results)
