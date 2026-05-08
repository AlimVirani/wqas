from wiki_qa.evals.dataset import CASES
from wiki_qa.evals.runner import run_cases
from wiki_qa.evals.reporting import summarize, dump_json

results = run_cases(CASES)
summarize(results)
dump_json(results, "results/latest.json")
