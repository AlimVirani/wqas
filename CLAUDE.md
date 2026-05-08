# Project: Wikipedia QA System

## What this is
A take-home assignment: a CLI that uses Claude + a Wikipedia search tool to
answer questions, plus an eval suite that measures answer quality.

## Code quality bar
- Python 3.11+, type hints on every function signature
- Small, single-purpose modules. No file over ~200 lines without a reason.
- Pure functions where possible; isolate I/O (API calls, file reads) at edges
- No premature abstraction. Two concrete uses before extracting an interface.
- Docstrings on public functions, terse comments only where the *why* isn't obvious

## Testing
- pytest, in a top-level `tests/` directory
- Unit-test the Wikipedia client and result formatting (mock HTTP)
- Unit-test the agent loop with a mocked Anthropic client
- Do NOT write tests that hit the real Anthropic or Wikipedia APIs in CI;
  those belong in the eval suite, not unit tests
- Aim for tests that would actually catch a regression, not coverage theater

## Project structure
src/
  wiki_qa/
    __init__.py
    cli.py          # argparse + main entry point
    agent.py        # the Claude tool-use loop
    wikipedia.py    # MediaWiki API client + result formatting
    prompts.py      # system prompt + tool definition (versioned constants)
    config.py       # model name, max_tokens, etc.
  evals/
    dataset.py      # test cases as a list of dataclasses
    graders.py      # rubric/judge functions
    runner.py       # runs system on dataset, collects metrics
tests/
  test_wikipedia.py
  test_agent.py
  test_graders.py

## Dependencies
anthropic, requests, pytest. That's it for now. Resist adding more.

## What NOT to do
- No async unless we hit a real need. Sequential is fine for this scope.
- No web framework, no database, no caching layer, no retry-with-backoff
  library. Plain code.
- No LangChain or similar. The whole point of this assignment is to write
  the agent loop ourselves.