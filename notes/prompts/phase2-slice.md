Phase 2 starts now. We're building a minimal vertical slice of the eval suite — one test case, one grader, one runner, one reporter, end-to-end. The point is to prove the pipeline works before we design the full dataset. Resist the urge to build more than what's specified below — bigger dataset, more graders, fancier output. We'll grow it deliberately in subsequent steps.
Read EVAL_NOTES.md first for context on what kinds of cases the full suite will eventually cover.
Structure
Create src/wiki_qa/evals/ as a sub-package:
src/wiki_qa/evals/
  __init__.py
  __main__.py        # enables `python -m wiki_qa.evals`
  dataset.py         # EvalCase dataclass + a list with ONE case
  graders.py         # one grader function
  runner.py          # runs cases through the agent, collects results
  reporting.py       # prints summary to stdout, writes JSON to disk
Dataclasses
In dataset.py:
python@dataclass(frozen=True)
class EvalCase:
    id: str
    question: str
    category: str
    expected_facts: list[str]  # case-insensitive substrings that should appear in the answer
Define CASES: list[EvalCase] with exactly one case for now — use the Australia capital case from EVAL_NOTES.md:
pythonEvalCase(
    id="capital_australia",
    question="What is the capital city of Australia?",
    category="simple_factual",
    expected_facts=["Canberra"],
)
Grader
In graders.py, one function:
pythondef fact_recall(case: EvalCase, result: AnswerResult) -> dict:
    """Returns {'passed': bool, 'matched': list[str], 'missing': list[str]}."""
Case-insensitive substring match of each expected_fact against result.answer. Passes iff all expected facts are present.
Runner
In runner.py:
python@dataclass
class CaseResult:
    case: EvalCase
    answer_result: AnswerResult
    grades: dict  # grader_name -> grade dict

def run_cases(cases: list[EvalCase]) -> list[CaseResult]:
    ...
For each case: call agent.answer(case.question), run fact_recall on the result, collect into a CaseResult. Print → running: <id> before each case and   pass /   fail after.
Reporter
In reporting.py: a summarize(results: list[CaseResult]) -> None that prints a small table (id, category, passed) and an overall pass rate. Plus dump_json(results, path: str) that writes a JSON file with each case's full data including the answer, searches used, and grades. Put JSON output under results/ (gitignore that directory except for a .gitkeep).
__main__.py
pythonfrom wiki_qa.evals.dataset import CASES
from wiki_qa.evals.runner import run_cases
from wiki_qa.evals.reporting import summarize, dump_json

results = run_cases(CASES)
summarize(results)
dump_json(results, "results/latest.json")
Verification
Run it end-to-end: .venv/bin/python -m wiki_qa.evals. Show me:

The directory tree of new files
The full stdout of the run
The contents of results/latest.json

Don't commit yet — I want to review first.