Phase 3: Prompt Iteration
We have a baseline run preserved at results/baseline.json. Now we iterate the system prompt twice and re-run evals to measure the effect.
Important: Two iterations. Execute one at a time. Wait for me to say "next" between them. Don't run both back-to-back.
For each iteration:

Make the prompt change in src/wiki_qa/prompts.py. Keep the v0 prompt available as a comment above the new version, so the diff is reviewable.
Run the full eval suite: .venv/bin/python -m wiki_qa.evals
Copy results/latest.json to results/iter_N.json (where N is the iteration number).
Show me both the full stdout and a focused diff against the previous run — specifically: which cases changed pass/fail status, and any case where searches count or query phrasing changed materially.

Iteration 1: Search-discipline tightening
Hypothesis: The baseline prompt instructs Claude to "search whenever you need a fact you are not confident about," but this leaves Claude room to skip search when it perceives a question as low-effort (the gold case). A more directive instruction should fix this.
Prompt change: Replace the current SYSTEM_PROMPT with a version that requires a search before every factual answer. Keep the rest of the prompt's character. Specifically, change the "search whenever you need a fact" sentence to something like:

"Always perform at least one Wikipedia search before answering any factual question, even when you believe you know the answer. Wikipedia is the source of record for this system."

The exact wording is your call — keep it concise, keep the tone consistent with the v0 prompt.
Predicted effect on evals:

gold_chemical_symbol should now search and pass search_behavior
camus_birth_country_language may or may not change — the question is whether more directive language pushes Claude to decompose more aggressively
Other cases should be largely unchanged

Verification target: gold_chemical_symbol flips from search_behavior: FAIL to PASS. If it doesn't, that's its own finding worth discussing.
Save the run as results/iter_1.json. Stop and wait for review before iteration 2.
Iteration 2: Epistemic calibration
Hypothesis: The baseline shows Claude will compensate for shallow retrieval by searching aggressively and synthesizing fragments into confident answers (the Versailles case). This is risky behavior when the retrieved evidence is structurally insufficient. A prompt instruction can teach Claude to distinguish "fully supported by retrieved text" from "partially supported / inferred from related articles" and to caveat or abstain accordingly.
Prompt change: Add language to the system prompt that asks Claude to:

Distinguish between facts directly stated in retrieved Wikipedia extracts and facts that require inference across multiple extracts
Caveat answers when the retrieved evidence is fragmentary or indirect
Abstain explicitly when the question requires information beyond what the retrieved extracts contain

Keep this addition concise (2-4 sentences). Don't bloat the prompt with examples.
Predicted effect on evals:

versailles_criticisms should either abstain (flipping honest_failure: FAIL → PASS) OR produce a noticeably more caveated answer (which the grader won't catch but which is visible in the JSON). Either is interesting.
Multi-hop cases should still pass — the change shouldn't destabilize them.
Lead-section-insufficient cases should be more reliably honest about their limits.
Risk: Claude may become over-cautious and start hedging on simple cases. Watch for this.

Verification target: Compare the versailles_criticisms answer text to baseline. The case may still fail the automated grader if it produces a hedged-but-not-explicitly-abstaining answer — that's expected. Read the answers, not just the grades.
Save the run as results/iter_2.json. Stop and wait for review.