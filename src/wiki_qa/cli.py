"""CLI entry point for the Wikipedia QA system."""
from __future__ import annotations

import argparse
import sys

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
        _run_question(line)


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
        _run_demo()
    elif args.question:
        _run_question(args.question)
    else:
        _run_repl()


if __name__ == "__main__":
    main()
