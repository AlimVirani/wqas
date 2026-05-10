

## Highest-leverage suggestions

1. **Structured citations.** Add `pageid: int` and `url: str` to `SearchResult`. Format tool results as numbered references with URLs. Makes citations first-class data instead of model-prompted text.

2. **Committed baseline eval summary** as a human-readable markdown file (e.g., `evals/baseline_summary.md`) so reviewers see results without running the suite themselves.

3. **Eval semantics polish:**
   - The `known_fact` category notes still frame search as "over-search"; under the strict-grounding policy, the framing should be "grounding discipline" instead.
   - `injection_microsoft` has `expected_facts=[]` which makes fact_recall trivially pass. Reconsider — adding `["Bill Gates", "Paul Allen"]` would actually grade the answer content.
   - `min_searches=2` on multi-hop cases penalizes legitimate single-search answers (Camus). Consider renaming the metric to "decomposition_behavior" or making the threshold case-specific.

4. **Tests for eval graders.** (Already done in this iteration — done.)

5. **DESIGN_RATIONALE.md.** Short doc covering system design, prompt design, eval design, what evals taught us, iterations made, what we'd do next, time spent. The assignment explicitly asks for rationale.

## Reviewer's overall read (positive feedback worth preserving)

The submission demonstrates judgment. Smallest useful system, unit tests, eval suite with 13 cases across categories (simple, known, multi-hop, ambiguous, adversarial, lead-section-insufficient), prompt that visibly evolved based on evals.

Clean architecture: `agent.py` owns the model/tool loop, `wikipedia.py` owns retrieval, `prompts.py` owns the system prompt and tool definition, CLI is separate. Wikipedia client is pragmatic — MediaWiki API, lead-section extracts, structured `SearchResult`, has a timeout.

Prompt evolution shows iteration: always-search policy, Wikipedia as source of record, distinguish direct evidence from inference, caveat fragmentary evidence, abstain when extracts don't support.

## Honest limitations the reviewer flagged (worth surfacing in rationale)

- Citations are article-level (model-prompted), not structured (URL/pageid/revision).
- Retrieval is lead-section-only — weak for "main criticisms," comparisons, causes, controversies.
- Substring fact_recall is a smoke test, can pass misleading answers (we already discovered this with python_ambiguous).
- search_behavior measures count, not query quality.
- Phrase-based honest_failure (now upgraded to LLM-judge) was rough.