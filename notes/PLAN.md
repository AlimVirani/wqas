# Build Plan

## Phase 1: Working skeleton
Goal: `python -m wiki_qa "Who wrote Pride and Prejudice?"` returns an answer.

Tasks (do in order, commit after each):
1. Wikipedia client in `wikipedia.py`: `search(query) -> list[SearchResult]`
   where SearchResult is a dataclass with `title` and `extract`. Tests with
   mocked `requests`.
2. Tool definition + minimal system prompt in `prompts.py`. The system
   prompt for Phase 1 should be deliberately simple — one paragraph. We
   improve it in Phase 3 based on eval data.
3. Agent loop in `agent.py`: `answer(question) -> AnswerResult` where
   AnswerResult has `answer`, `searches` (list of queries used), and
   `messages` (full conversation). Tests with a mocked Anthropic client
   that returns a scripted tool_use then end_turn.
4. CLI in `cli.py`: positional question arg, `--demo` flag, `--verbose`
   flag that prints search queries as they happen.
5. README with setup + sample invocations.

Done when: demo mode runs end-to-end against real APIs and produces
reasonable answers for 3 sample questions.

## Phase 2: Eval harness
Goal: `python -m evals` runs the system on a test set and prints scores.

Tasks:
1. Define ~15 test cases in `evals/dataset.py` as dataclasses. Categories:
   - Simple factual (5)
   - Multi-hop requiring 2+ searches (3)
   - Should-not-search (Claude already knows it) (2)
   - Ambiguous/needs disambiguation (2)
   - Unanswerable / out-of-scope (2)
   - Time-sensitive / Wikipedia-may-not-have (1)
   Each case: question, category, expected_facts (list of strings that
   should appear), should_search (bool), notes.
2. Graders in `evals/graders.py`:
   - `fact_recall`: do the expected_facts appear in the answer? (string match)
   - `search_appropriateness`: did searching happen iff should_search? (bool)
   - `llm_judge`: Claude-as-judge scoring answer quality 1-5 with rationale
3. Runner in `evals/runner.py`: runs each case, collects results, prints a
   table + per-category breakdown + saves JSON for later comparison.

Done when: we have a baseline score and a saved `baseline.json`.

## Phase 3: Iterate prompt
Goal: 2-3 documented prompt revisions, each justified by eval data.

Process per iteration:
1. Look at the failure cases from the previous run
2. Form a hypothesis about what prompt change would fix them
3. Make the change (keep old version in `prompts.py` history as a comment
   or git tag so we can compare)
4. Re-run evals, save as `iter_N.json`
5. Write 2-3 sentences in `ITERATIONS.md` about what changed and why

Stop after 3 iterations or when scores plateau.