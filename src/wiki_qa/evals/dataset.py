"""Eval cases for the Wikipedia QA system."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EvalCase:
    id: str
    question: str
    category: str
    expected_facts: list[str]


CASES: list[EvalCase] = [
    EvalCase(
        id="capital_australia",
        question="What is the capital city of Australia?",
        category="simple_factual",
        expected_facts=["Canberra"],
    ),
]
