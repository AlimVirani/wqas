"""CLI entry point for the Wikipedia QA system."""
from __future__ import annotations

import argparse
import sys

import anthropic
import requests

from wiki_qa import agent

DEMO_QUESTIONS = [
    # Simple factual — Claude may know but should verify
    "What is the capital city of Australia?",
    # Multi-hop — requires at least two searches to connect the facts
    "Who invented the telephone, and what university did their father attend?",
    # Claude almost certainly knows this without searching
    "What is the speed of light in a vacuum?",
]


def _on_search(query: str) -> None:
    print(f"→ searching: '{query}'")


def _handle_error(e: Exception, exit_on_error: bool = False) -> None:
    if isinstance(e, requests.exceptions.RequestException):
        print(
            f"Error: Wikipedia request failed ({e}). Try again or check your connection.",
            file=sys.stderr,
        )
    elif isinstance(e, anthropic.APIError):
        print(
            f"Error: Anthropic API request failed ({e}). Check your ANTHROPIC_API_KEY.",
            file=sys.stderr,
        )
    else:
        print(f"Error: {e}", file=sys.stderr)
    if exit_on_error:
        sys.exit(1)


def _run_question(question: str) -> None:
    result = agent.answer(question, on_search=_on_search)
    print(result.answer)
    print(f"[searches used: {len(result.searches)}]")


def _run_demo() -> None:
    for i, question in enumerate(DEMO_QUESTIONS, 1):
        print(f"\n--- Question {i} ---")
        print(question)
        print()
        _run_question(question)


def _run_repl() -> None:
    print("Wikipedia QA — type a question, or enter 'quit', 'exit', or an empty line to stop.")
    while True:
        try:
            line = input("\nQuestion: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line or line.lower() in {"quit", "exit"}:
            break
        try:
            _run_question(line)
        except Exception as e:
            _handle_error(e)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="wiki_qa",
        description="Answer questions using Claude + Wikipedia.",
    )
    parser.add_argument(
        "question",
        nargs="?",
        help="Question to answer (exits after printing the answer).",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run a set of sample questions and exit.",
    )
    args = parser.parse_args()

    if args.demo:
        try:
            _run_demo()
        except Exception as e:
            _handle_error(e, exit_on_error=True)
    elif args.question:
        try:
            _run_question(args.question)
        except Exception as e:
            _handle_error(e, exit_on_error=True)
    else:
        _run_repl()


if __name__ == "__main__":
    main()
