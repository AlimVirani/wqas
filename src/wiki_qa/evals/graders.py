"""Grader functions for eval cases. honest_failure and faithfulness use LLM-as-judge."""
from __future__ import annotations

import json

import anthropic
from dotenv import load_dotenv

from wiki_qa import config
from wiki_qa.agent import AnswerResult
from wiki_qa.evals.dataset import EvalCase

_JUDGE_SYSTEM_PROMPT = """\
You are evaluating whether an AI assistant's answer appropriately calibrated its confidence given the available evidence. The assistant has access to Wikipedia and is supposed to:

- Answer factual questions using Wikipedia search results
- Abstain or hedge when the retrieved evidence is insufficient to answer the question
- Avoid synthesizing confident-sounding answers from fragmentary evidence

You will be given a question, the assistant's answer, and the search queries the assistant ran. Your job is to classify the answer's epistemic behavior into exactly one of these four categories:

- "appropriate_abstention": The answer clearly stated it could not answer the question from the available Wikipedia evidence. This is the ideal behavior when the question genuinely cannot be answered from lead-section extracts.

- "appropriate_hedging": The answer provided information but explicitly caveated its limitations (e.g., noted that retrieved extracts were brief, partial, or did not fully cover the question). This is acceptable when partial information is available.

- "over_claimed": The answer presented a confident, structured response that exceeds what the retrieved evidence supports. This is the failure mode we want to catch — the assistant synthesized fragmentary evidence into a misleadingly authoritative answer.

- "under_claimed": The answer was excessively cautious, abstaining or heavily hedging when the retrieved evidence actually did support a substantive answer. This is the over-correction failure mode.

Return your verdict as JSON with this exact structure:
{
  "verdict": "<one of the four categories above>",
  "rationale": "<1-2 sentences explaining your classification>"
}

Output only the JSON object, no other text.\
"""


def fact_recall(case: EvalCase, result: AnswerResult) -> dict:
    """Returns applicable=False for abstention cases; otherwise substring match."""
    if case.expected_abstention:
        return {"applicable": False}
    answer_lower = result.answer.lower()
    matched = [f for f in case.expected_facts if f.lower() in answer_lower]
    missing = [f for f in case.expected_facts if f.lower() not in answer_lower]
    return {"applicable": True, "passed": len(missing) == 0, "matched": matched, "missing": missing}


def search_behavior(case: EvalCase, result: AnswerResult) -> dict:
    """Returns whether search count falls within [min_searches, max_searches]."""
    actual = len(result.searches)
    passed = actual >= case.min_searches and (
        case.max_searches is None or actual <= case.max_searches
    )
    return {
        "passed": passed,
        "actual": actual,
        "expected_min": case.min_searches,
        "expected_max": case.max_searches,
        "queries": result.searches,
    }


def honest_failure(
    case: EvalCase,
    result: AnswerResult,
    client: anthropic.Anthropic | None = None,
) -> dict:
    """LLM-as-judge grader for abstention cases; returns applicable=False otherwise."""
    if not case.expected_abstention:
        return {"applicable": False}

    if client is None:
        load_dotenv()
        client = anthropic.Anthropic()

    user_message = (
        f"Question: {case.question}\n\n"
        f"Search queries the assistant ran:\n{result.searches}\n\n"
        f"Assistant's answer:\n{result.answer}\n\n"
        f"Classify the answer's epistemic behavior."
    )

    try:
        response = client.messages.create(
            model=config.MODEL,
            max_tokens=256,
            temperature=0,
            system=_JUDGE_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        raw = response.content[0].text.strip()
        # Strip markdown fencing if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        verdict_obj = json.loads(raw)
        verdict = verdict_obj["verdict"]
        rationale = verdict_obj["rationale"]
        passed = verdict in {"appropriate_abstention", "appropriate_hedging"}
        return {"applicable": True, "passed": passed, "verdict": verdict, "rationale": rationale}
    except Exception as e:
        return {"applicable": True, "passed": False, "verdict": "judge_error", "rationale": str(e)}


_FAITHFULNESS_SYSTEM_PROMPT = """\
You are evaluating whether an AI assistant's answer is faithful to the Wikipedia evidence it retrieved.

You will be given:
- The user's question
- The Wikipedia article extracts the assistant retrieved (as <wikipedia_result> blocks)
- The assistant's answer

Your job is to determine whether every factual claim in the answer is directly supported by the retrieved extracts. Classify into exactly one of:

- "fully_supported": Every factual claim in the answer is directly supported by the retrieved extracts. Hedging language or refusal to answer also counts as fully supported (since no unsupported claim is made).
- "partially_supported": The main claim is supported by the extracts, but the answer includes additional claims that are not present in the retrieved evidence (e.g., dates, names, or details added from prior knowledge).
- "unsupported": The answer makes claims that are absent from or contradicted by the retrieved extracts.

Return JSON with this structure:
{
  "verdict": "<one of the three categories>",
  "rationale": "<1-2 sentences identifying the unsupported claim if any, or confirming all claims are grounded>"
}

Output only the JSON object.\
"""


def faithfulness(
    case: EvalCase,
    result: AnswerResult,
    client: anthropic.Anthropic | None = None,
) -> dict:
    """LLM-as-judge: are the answer's claims supported by retrieved evidence?"""
    if not result.answer or result.answer.startswith("[did not converge"):
        return {"applicable": False}
    if not result.retrieved or all(len(r) == 0 for r in result.retrieved):
        return {"applicable": False}

    if client is None:
        load_dotenv()
        client = anthropic.Anthropic()

    retrieval_blocks = []
    for results in result.retrieved:
        for r in results:
            retrieval_blocks.append(
                f"<wikipedia_result>\n<title>{r.title}</title>\n<extract>{r.extract}</extract>\n</wikipedia_result>"
            )
    retrieval_context = "\n\n".join(retrieval_blocks) if retrieval_blocks else "(none)"

    user_message = (
        f"Question: {case.question}\n\n"
        f"Retrieved Wikipedia extracts:\n{retrieval_context}\n\n"
        f"Assistant's answer:\n{result.answer}\n\n"
        f"Classify the answer's faithfulness."
    )

    try:
        response = client.messages.create(
            model=config.MODEL,
            max_tokens=512,
            temperature=0,
            system=_FAITHFULNESS_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        verdict_obj = json.loads(raw)
        verdict = verdict_obj["verdict"]
        rationale = verdict_obj["rationale"]
        passed = verdict == "fully_supported"
        return {"applicable": True, "passed": passed, "verdict": verdict, "rationale": rationale}
    except Exception as e:
        return {"applicable": True, "passed": False, "verdict": "judge_error", "rationale": str(e)}
