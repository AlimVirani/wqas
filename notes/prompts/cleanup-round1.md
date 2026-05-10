Cleanup Round 1: code hygiene, no behavior change
Five small changes. None should affect runtime behavior. After all changes, all 27 existing tests must still pass.
1. Remove commented prompt versions from prompts.py
The v0 and v1 prompts are currently preserved as block comments above the active SYSTEM_PROMPT. Remove them. The historical record lives in git history and in the results/v*_judge.json files; source code shouldn't be a museum.
Keep the active v2 SYSTEM_PROMPT and SEARCH_WIKIPEDIA_TOOL exactly as they are. Just delete the commented blocks.
2. Add module-level docstrings
Each file under src/wiki_qa/ should start with a one-line docstring describing what the module does. Specifically:

agent.py: "Claude tool-use loop. See answer() for the entry point."
cli.py: "Command-line interface: positional question, --demo flag, or interactive REPL."
wikipedia.py: "MediaWiki API client. One public function: search()."
prompts.py: "System prompt and tool-definition constants."
config.py: "Runtime configuration constants."
evals/dataset.py: "Eval cases and the EvalCase dataclass."
evals/graders.py: "Grader functions for eval cases. honest_failure uses LLM-as-judge."
evals/runner.py: "Runs eval cases through the agent and collects graded results."
evals/reporting.py: "Summary table and JSON output for eval results."

If a module already has a docstring, leave it alone (don't double up).
3. Tighten type annotations
Replace bare dict and list with parameterized versions where the shape is known. Specifically:

In agent.py, AnswerResult.messages: list → list[dict]
In prompts.py, SEARCH_WIKIPEDIA_TOOL: dict → dict[str, object] (the schema is heterogeneous, so object is honest)
In evals/runner.py, CaseResult.grades: dict → dict[str, dict]
In any grader function returning dict, leave them alone — the return shapes are documented in docstrings already

Don't introduce TypedDicts. The marginal benefit doesn't justify the boilerplate at this scale.
4. Move _format_results from agent.py to wikipedia.py
Currently agent.py has a private _format_results(results: list[SearchResult]) -> str function that builds the string Claude sees from a list of SearchResult objects. This is output formatting for the Wikipedia data, and it belongs next to the data structure.
Move the function to wikipedia.py. Make it public (rename to format_results) since agent.py will need to import it. Update the import in agent.py accordingly. No signature or behavior change.
5. Make USER_AGENT private
In wikipedia.py, rename USER_AGENT → _USER_AGENT to match the existing _API_URL convention. Both are module-private implementation details.
Add a one-line comment above it: # Wikipedia's User-Agent policy requires identifying contact info.
Verification
Run all tests: .venv/bin/python -m pytest tests/ -q
All 27 tests must pass with no changes. If any test breaks, you've changed behavior — stop and tell me what broke.
Show me a unified diff (git diff) of all changes plus the test output.
