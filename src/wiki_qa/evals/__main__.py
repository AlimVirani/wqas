import argparse

from wiki_qa.evals.dataset import CASES
from wiki_qa.evals.reporting import dump_json, summarize
from wiki_qa.evals.runner import run_cases

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
