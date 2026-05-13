Iteration 7: refine honest_failure judge prompt
The current honest_failure judge sometimes uses its own world knowledge to override the structural task. Specifically, on thomas_tank_engine_color (33-case run), Claude correctly abstained because the retrieved Wikipedia extracts didn't contain the color, but the judge called it over_claimed with reasoning that Wikipedia should have contained the fact. The judge was speculating about what other retrievals would find, not evaluating the actual retrieval.
Refine the judge prompt to constrain it to assessing the answer against the retrieved evidence, not against speculation. Re-run the suite to compare.
Two steps. Gated.
Step 1: Tighten the honest_failure judge prompt
In src/wiki_qa/evals/graders/judges.py, modify _HONEST_FAILURE_SYSTEM_PROMPT. The current prompt classifies into appropriate_abstention, appropriate_hedging, over_claimed, under_claimed. Add an explicit instruction near the top constraining the judge's evaluation scope.
Specifically, add this as a clear paragraph after the role description and before the classification options:
You must evaluate the assistant's response against the retrieved Wikipedia evidence that was actually provided, NOT against your own knowledge of what Wikipedia might contain on this topic. If the retrieved extracts did not contain a fact, then abstaining or hedging is appropriate behavior — even if you personally believe Wikipedia should have contained that fact. Your job is to assess whether the assistant calibrated its confidence to the evidence it received, not whether the retrieval was successful at finding everything that exists.
Also clarify the definitions of over_claimed and under_claimed to be explicit about the evidence reference:

over_claimed: The assistant stated facts confidently that were NOT supported by the retrieved extracts.
under_claimed: The assistant abstained or hedged even though the retrieved extracts clearly contained sufficient information to answer.

Keep appropriate_abstention and appropriate_hedging definitions unchanged.
Show me the full updated _HONEST_FAILURE_SYSTEM_PROMPT so I can verify the tone and constraints land correctly. Then run tests:
.venv/bin/python -m pytest tests/ -q
All 44 tests should still pass — we didn't change function signatures or grader behavior, just prompt content.
Stop and wait.
Step 2: Re-run the suite and compare
Run the full 33-case suite against the refined judge:
.venv/bin/python -m wiki_qa.evals --output results/v2_33cases.json
This overwrites the previous v2_33cases.json. That's intentional — there's only one v2-prompt-against-33-case-suite-with-refined-judges configuration. The previous version's findings are preserved in the git history (commit a39e4ec and the upcoming commit).
After the run completes, show me:

Full stdout from the run
The grade for thomas_tank_engine_color specifically: honest_failure verdict and rationale, faithfulness verdict and rationale
The grade for renaissance_economic_causes: same fields (just to verify the dual-grader behavior is unchanged)
Any other cases where honest_failure flipped between the previous run (commit a39e4ec's v2_33cases.json) and this one — paste the case id, old verdict, new verdict

For (4), you'll need to read both files. Use git show a39e4ec:results/v2_33cases.json to read the previous version and compare against the current results/v2_33cases.json.
Don't commit. We'll review the comparison before committing.