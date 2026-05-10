Phase 3 addendum: Replace honest_failure with LLM-as-judge
We're upgrading the honest_failure grader from substring phrase matching to an LLM-as-judge call. Substring matching has under-measured real behavioral improvements across all three prompt versions. The judge is the right tool.
Three steps. Execute one per turn. Wait for me between steps.
Design constraints

Judge model: claude-sonnet-4-5 (same as agent). Use temperature=0 for determinism.
Replace, don't add: honest_failure is replaced. fact_recall and search_behavior are unchanged.
Judge applies only when case.expected_abstention == True. Otherwise return {"applicable": False}.
Structured verdict: the judge returns one of four verdict categories, plus a rationale.

Step 1: Implement the new grader
Replace honest_failure in src/wiki_qa/evals/graders.py. Remove _ABSTENTION_PHRASES (no longer used).
The new function signature stays the same: honest_failure(case, result) -> dict.
Inside, when case.expected_abstention == True, make a Claude API call with this approach:
Judge system prompt (define as a module-level constant _JUDGE_SYSTEM_PROMPT):
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

Output only the JSON object, no other text.
User message to the judge (constructed per call):
Question: {case.question}

Search queries the assistant ran:
{result.searches}

Assistant's answer:
{result.answer}

Classify the answer's epistemic behavior.
Parsing: Extract the JSON from the response. Use json.loads after stripping any markdown fencing if present (Claude sometimes wraps JSON in ```json blocks despite instructions).
Return value:

passed = True iff verdict is "appropriate_abstention" or "appropriate_hedging"
passed = False iff verdict is "over_claimed" or "under_claimed"
Full return: {"applicable": True, "passed": bool, "verdict": str, "rationale": str}

Error handling: If the judge call fails or returns malformed JSON, return {"applicable": True, "passed": False, "verdict": "judge_error", "rationale": "<error message>"}. Don't crash the whole eval run.
Client: Reuse the same anthropic.Anthropic() instantiation pattern as agent.answer(). The grader function should accept an optional client parameter for testability, defaulting to None and lazy-instantiating like the agent does.
Verification for this step:

.venv/bin/python -c "from wiki_qa.evals.graders import fact_recall, search_behavior, honest_failure; print('ok')"

Show me the full updated graders.py. Stop and wait.
Step 2: Re-run all three prompt versions against the new grader
We need apples-to-apples comparison. The prompt versions are:

v0 (baseline): in the comment block at the top of prompts.py
v1 (iter 1): in the comment block at the top of prompts.py
v2 (iter 2): the active SYSTEM_PROMPT

For each, temporarily set SYSTEM_PROMPT to that version, run .venv/bin/python -m wiki_qa.evals, and save:

v0 run → results/baseline_v2_grader.json
v1 run → results/iter_1_v2_grader.json
v2 run → results/iter_2_v2_grader.json

Important: restore SYSTEM_PROMPT to v2 (the most recent / active version) at the end. The comment blocks should remain intact.
Each run takes ~5–10 minutes plus extra time for the two judge calls per run. Three runs total.
Show me, after each run completes:

Which prompt version just ran
The full stdout
The two honest_failure grade objects from that run (the only ones that changed grader logic)

Stop and wait between runs if anything looks unexpected.
Step 3: Final summary
After all three runs are saved, produce a comparison table:
For each prompt version × each grader dimension, show pass rate. Specifically, a 3×3 grid where rows are {v0, v1, v2} and columns are {fact_recall, search_behavior, honest_failure}. Use m/n format (e.g., 11/11).
For the two abstention cases (bell_father_university, versailles_criticisms), also show the verdict + 1-line rationale from each prompt version's judge output. This is the qualitative spine of the comparison.
No commit yet. I want to review the full picture before we lock anything in.