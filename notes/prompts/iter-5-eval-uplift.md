Iteration 5: Eval suite refactor and ergonomics
Five changes coordinated as one refactor. Execute in order, gated. Wait between steps.
Important: This is purely a refactor + UX pass. No prompt changes, no behavior changes to the system being evaluated. After all steps, the same evals should produce equivalent grade decisions — just organized, packaged, and presented better.
Step 1: Split graders.py into a package
Restructure to align the file layout with the runtime split (fast automated vs. slow LLM-judge).
Create src/wiki_qa/evals/graders/ as a package:
src/wiki_qa/evals/graders/
  __init__.py    # re-exports the public functions
  automated.py   # fact_recall, search_behavior
  judges.py      # honest_failure, faithfulness, judge prompts
automated.py: contains fact_recall and search_behavior only. Pure functions, no Anthropic imports.
judges.py: contains honest_failure, faithfulness, and both _*_SYSTEM_PROMPT constants. All LLM-as-judge code lives here.
__init__.py: re-exports so existing imports (from wiki_qa.evals.graders import fact_recall, search_behavior, honest_failure, faithfulness) keep working unchanged:
pythonfrom wiki_qa.evals.graders.automated import fact_recall, search_behavior
from wiki_qa.evals.graders.judges import honest_failure, faithfulness

__all__ = ["fact_recall", "search_behavior", "honest_failure", "faithfulness"]
Delete the original src/wiki_qa/evals/graders.py.
Verification:

.venv/bin/python -m pytest tests/ -q — all 33 tests pass (imports resolve through the new __init__.py)
.venv/bin/python -c "from wiki_qa.evals.graders import fact_recall, search_behavior, honest_failure, faithfulness; print('ok')" — confirms backward-compatible imports

Show me the new directory tree and test output. Stop and wait.
Step 2: Add CLI flags for which graders to run
Modify src/wiki_qa/evals/__main__.py to accept argparse flags:

--fast: run only automated graders (fact_recall, search_behavior). No LLM calls. Skips honest_failure and faithfulness.
--judges-only: run only LLM-judge graders. Useful for re-grading existing results without re-running the agent (though for v1 we'll just rerun the whole thing — flag is for future use).
(default, no flag): run everything.

The way to implement this cleanly: pass a graders selector down to run_cases. Update run_cases(cases, *, run_judges: bool = True, run_automated: bool = True) -> list[CaseResult]. Inside, only call the relevant grader functions. For skipped graders, the grades dict simply omits that key (rather than putting applicable=False, since "we didn't run it" is different from "doesn't apply").
The reporter (summarize, dump_json) should handle missing grader keys gracefully — display – (or some indicator) for "not run" in the table.
Update __main__.py:
pythonimport argparse
from wiki_qa.evals.dataset import CASES
from wiki_qa.evals.runner import run_cases
from wiki_qa.evals.reporting import summarize, dump_json

parser = argparse.ArgumentParser(description="Run the wiki_qa eval suite.")
parser.add_argument("--fast", action="store_true",
                    help="Run only fast automated graders (no LLM calls).")
parser.add_argument("--judges-only", action="store_true",
                    help="Run only LLM-judge graders.")
parser.add_argument("--output", default="results/latest.json",
                    help="Path to write JSON results.")
args = parser.parse_args()

if args.fast and args.judges_only:
    parser.error("--fast and --judges-only are mutually exclusive")

run_automated = not args.judges_only
run_judges = not args.fast

results = run_cases(CASES, run_automated=run_automated, run_judges=run_judges)
summarize(results)
dump_json(results, args.output)
Verification:

.venv/bin/python -m wiki_qa.evals --help — shows flags
.venv/bin/python -m pytest tests/ -q — all tests pass

Show me --help output and test results. Stop and wait. (Don't actually run the suite yet — Step 4 verifies end-to-end.)
Step 3: Unit tests for automated graders
Add tests/test_automated_graders.py with unit tests for fact_recall and search_behavior. Both are pure functions; no mocking needed except constructing fixture EvalCase and AnswerResult objects.
Tests to write:
fact_recall:

Returns {"applicable": False} when case.expected_abstention=True
Returns passed=True when all expected_facts appear in the answer
Returns passed=False when one or more expected_facts are missing
Case-insensitive matching (uppercase fact, lowercase answer → matches)
Empty expected_facts list → passes (no facts to check)

search_behavior:

Passes when len(searches) >= min_searches and within max_searches
Fails when len(searches) < min_searches
Fails when max_searches is set and len(searches) > max_searches
Passes with max_searches=None regardless of search count (as long as min is met)
Returns the full query list in the result

Aim for ~10 tests total. Each ~5 lines. These are trivial functions; the tests are insurance against future refactor breakage.
Verification:

.venv/bin/python -m pytest tests/ -q — all tests pass (count grows by ~10 from 33)

Show me the new test file (or its key bodies — first and last test functions are enough) and the test count. Stop and wait.
Step 4: Redesign the output
Current output is wide, loud, and hard to scan. Redesign with these principles:

Summary first, details second. The summary line at the top is the most important info; it should appear before the per-case table, not after.
Symbols, not words. ✓ for pass, ✗ for fail, · for n/a, − for not run. Each is one character; the table compresses massively.
Group by category. Cases within a category appear together with a one-line header.
Drop the verbose category column. It's implied by the grouping.

Example target output:
Wikipedia QA eval suite — 24 cases, 4 graders

  fact_recall      ✓✓✓✓ ✓✓ ✓✓✓·· ····· ✓✓✓ ··    17/19
  search_behavior  ✓✓✗✓ ✓✓ ✓✗✓✓✓ ✓✓✓✓✓ ✓✓✓ ✓✓✗   21/24
  honest_failure   ···· ·· ····· ✓✓✓✓✓ ··· ···   5/5
  faithfulness     ✓✓·✓ ✓✓ ✓✗✓✓✓ ····· ✓✓✓ ✓·−   19/22

By case:

simple_factual (4)
  ✓✓✓✓  capital_australia            fact:✓ search:✓ honest:·  faith:✓
  ✓✓✓✓  author_pride_prejudice       fact:✓ search:✓ honest:·  faith:✓
  ...

known_fact (4)
  ...

[etc.]

Per-category pass rates:
  simple_factual      fact:4/4  search:3/4  honest:n/a  faith:4/4
  known_fact          fact:2/2  search:2/2  honest:n/a  faith:2/2
  ...
The exact formatting can vary — what matters is: summary on top, symbols throughout, grouped by category, narrower than the current wall-of-text.
Implement in src/wiki_qa/evals/reporting.py. The function signature stays the same (summarize(results) -> None).
Verification: run the suite end-to-end:
bash.venv/bin/python -m wiki_qa.evals --fast
--fast is meaningful here — it lets us verify the new output format without spending 15 minutes on LLM judges. Show me the full stdout from this run. The summary should clearly show fact_recall and search_behavior results, with honest_failure and faithfulness showing as "not run" / −.
Stop and wait.
Step 5: Update README
Add a new "Running evals" section to the main README.md, between "Usage" and "Running tests". Content:
markdown## Running evals

The eval suite measures system quality across four dimensions: factual correctness, search behavior, honest failure (LLM-judge), and faithfulness to retrieved evidence (LLM-judge).

Run everything:
    .venv/bin/python -m wiki_qa.evals

Fast mode — only the automated graders, no LLM calls (~30 seconds vs ~15 minutes):
    .venv/bin/python -m wiki_qa.evals --fast

Results are written to `results/latest.json` by default. Historical runs across prompt versions live in `results/v*.json` — see `results/README.md` for details.
Also update the "Project structure" section in the README to reflect:

src/wiki_qa/evals/ exists with its modules
src/wiki_qa/evals/graders/ is a sub-package

Verification:

The README renders correctly (Claude Code can just paste back the relevant sections; I'll eyeball).

Show me the updated sections of the README. Stop.