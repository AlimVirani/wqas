Task: write results/README.md
Write a reference document for the results/ directory. Job: a reviewer landing on this folder with no prior context can quickly understand what each file represents and how to read it.
Critical constraint: every factual claim in this document must be verified against the actual files in results/. Do not paraphrase or guess. If you state a pass rate, open the corresponding JSON and confirm it. If you describe a file's structure, view the file first. If a section requires data you can't confirm, leave it as [TODO: verify] rather than inventing a number.
This is reference documentation, not narrative or rationale. It should be scannable, not story-shaped.
Required sections
1. Overview (~3 sentences)
What this directory contains and why. Mention that the JSON files are eval-suite outputs across different prompt versions, grader configurations, and suite generations. State which file is the current canonical baseline (v2_33cases.json).
2. File naming convention
Explain the naming scheme. Three axes have varied across iterations:

Prompt version (v0, v1, v2) — versions of the system prompt. There is no v3 in the final set — a v3 was attempted and rolled back; that history is in commit logs.
Grader type (substring, judge) — older results used phrase-based substring matching for honest_failure; later results use LLM-as-judge.
Suite generation (24cases, 33cases) — the eval suite grew from 13 → 24 → 33 cases over iterations.

Show the current set of files with one-line descriptions. View the directory first to confirm the list. Format as a table or list, not prose.
3. Iteration timeline
Brief — a few sentences or a small table. For each prompt version (v0 / v1 / v2), state in one line what changed and link to the corresponding results file. Do not editorialize; just state what the prompt version was about and which file holds its results.
The pattern:

v0: baseline minimal prompt
v1: added strict-grounding policy ("always search")
v2: added epistemic calibration (distinguish stated facts from inferred, abstain when extracts insufficient)

4. JSON structure
Document the structure of a single case entry in the current canonical file (v2_33cases.json). View one entry from the file before writing this section. Cover:

Top-level fields per case (id, question, category, bucket, notes, answer, searches, retrieved, grades)
What's in retrieved (parallel to searches; list of lists of {title, extract})
What's in grades — show the four grader keys and the structure of each grader's result object (applicable, passed, plus grader-specific fields like verdict and rationale for the LLM judges)

Include a brief example showing one case's grades object trimmed to ~10 lines.
5. Current baseline
For v2_33cases.json, state the headline numbers:

Total cases: 33 (13 base / 7 product / 13 hard — verify counts by reading the file)
Pass rates per grader (read from the file; do not invent)
The three buckets and what they represent

Then a short subsection (~5 lines) noting the most interesting findings in the current baseline. Not analysis — just pointing at where the interesting data lives. E.g., "safety cases (firearm, self-harm, TV-show calibration) test refusal behavior; see cases safety_firearm_harm, safety_self_harm, safety_calibration_tv_show." "Faithfulness failures cluster on multi-hop product cases (Camus, Darwin) — see those cases in the file for the prior-knowledge bleed pattern."
6. Graders
One short paragraph per grader explaining what it measures. Source from the grader files in src/wiki_qa/evals/graders/.

fact_recall — automated. Substring match (Unicode-normalized) of expected_facts against the answer. Returns applicable: False for abstention cases.
search_behavior — automated. Checks len(searches) against min_searches/max_searches. Used for both "search at least N times" and the safety bucket's "must not search."
honest_failure — LLM-as-judge (claude-sonnet-4-5). Classifies into appropriate_abstention, appropriate_hedging, over_claimed, under_claimed. Applicable only to abstention cases.
faithfulness — LLM-as-judge. Classifies into fully_supported, partially_supported, unsupported. Applicable to any case where the agent produced an answer with retrieved extracts.

7. Reproducing the baseline
Two lines:

Full run: python -m wiki_qa.evals --output results/<your_filename>.json
Fast (automated only): python -m wiki_qa.evals --fast --output results/<your_filename>.json

Note that LLM-judge runs require ANTHROPIC_API_KEY in environment and cost ~15-20 minutes per 33-case run; fast mode runs in ~30 seconds.
Style guidelines

Markdown. Use headers, lists, and small tables where they help scanability.
Keep section bodies short. A reader should be able to scan the whole file in under two minutes.
No editorial language. No "we believe" / "the system gracefully handles" — this is reference, not pitch.
Code paths and filenames in backticks.
No emoji, no decorative formatting.

Process

First, view results/ to confirm the exact file list.
Then view results/v2_33cases.json (or a slice of it) to confirm JSON structure.
Compute the headline numbers from the file directly. Do not estimate.
Then draft the document.
After drafting, re-read it as if you've never seen the project. Does every claim have a source? Is anything unclear? Revise.

Save the result to results/README.md. Then show me the full document inline so I can review it without opening the file.
Don't commit. We'll review before committing.