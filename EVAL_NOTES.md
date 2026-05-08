# Eval Seed Cases — Phase 1 Baseline

Captured from the first end-to-end demo run. These are real observations of
the baseline prompt's behavior and will inform the Phase 2 eval dataset.

## Case 1: Simple factual — works as expected
- **Question:** "What is the capital city of Australia?"
- **Searches:** 1 (`'capital city Australia'`)
- **Answer:** Correct (Canberra), with citation
- **Behavior to measure:** Single-search efficiency, correct citation

## Case 2: Multi-hop with hidden architectural limit
- **Question:** "Who invented the telephone, and what university did their father attend?"
- **Searches:** 5 (telephone invention → A.G. Bell → A.M. Bell → A.M. Bell education → A.M. Bell U. of Edinburgh)
- **Answer:** Got A.G. Bell and A.M. Bell correctly, but reported it could not find the university in Wikipedia's lead-section extracts. Honest failure rather than confabulation.
- **Why this matters:** Our tool returns `exintro=True` lead sections only. Detailed biographical facts (attended X university) typically live in body paragraphs, not the lead. So Claude can search correctly and still not get the data. This is an architectural limit of the retrieval tool, not a prompt issue.
- **Open question for Phase 3:** Accept the limit, extend extracts beyond the lead, or add a `get_full_article(title)` tool?

## Case 3: Should-not-search — over-searched
- **Question:** "What is the speed of light in a vacuum?"
- **Searches:** 1 (Claude searched despite knowing the answer)
- **Answer:** Correct, well-formatted
- **Why this matters:** The minimal system prompt told Claude to search "whenever you need a fact you are not confident about." Claude apparently isn't confident enough about a defined SI constant to skip the search. This is a prompt-engineering target for Phase 3 — measure search-appropriateness as an eval dimension.

## Implications for the eval dataset
- Need at least one case in each of: simple-factual (passes), multi-hop where Wikipedia lead doesn't have the answer (architectural limit), should-not-search (over-search baseline).
- Need a grader for "did the system search when it should have / not search when it shouldn't have."
- Need a grader that distinguishes honest "I don't know" failures (good) from confabulated wrong answers (bad).
