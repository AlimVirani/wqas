# Wikipedia QA

A CLI that uses Claude + Wikipedia to answer questions. The agent loop calls the
MediaWiki API as a tool whenever it needs a fact, then synthesises an answer with
citations. Built as a take-home assignment.

## Setup

```bash
git clone https://github.com/AlimVirani/wqas.git
cd wqas
python3.11 -m venv .venv
.venv/bin/pip install -e .
```

Set your Anthropic API key — either in a `.env` file:

```
ANTHROPIC_API_KEY=sk-ant-...
```

or as a shell export:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

## Usage

**Answer a single question and exit:**

```bash
.venv/bin/python -m wiki_qa "What is the capital city of Australia?"
```

```
→ searching: 'capital city Australia'
The capital city of Australia is **Canberra**. According to the Wikipedia article
on the "Australian Capital Territory," Canberra is situated within the ACT...
[searches used: 1]
```

**Run the built-in demo (three sample questions):**

```bash
.venv/bin/python -m wiki_qa --demo
```

```
--- Question 1 ---
What is the capital city of Australia?

→ searching: 'capital city Australia'
The capital city of Australia is **Canberra**...
[searches used: 1]

--- Question 2 ---
...
```

**Interactive REPL:**

```bash
.venv/bin/python -m wiki_qa
```

```
Wikipedia QA — type a question, or enter 'quit', 'exit', or an empty line to stop.

Question: What is the capital city of Australia?
→ searching: 'capital city Australia'
The capital city of Australia is **Canberra**.

According to the Wikipedia article on the "Australian Capital Territory," Canberra
is the capital city of Australia and is situated within the Australian Capital
Territory (ACT). The article on "List of Australian capital cities" also confirms
that Canberra is the national capital, noting that Section 125 of the Constitution
of Australia specified the national capital would be in its own territory within
New South Wales, at least 100 miles from Sydney.
[searches used: 1]

Question: quit
```

## Project structure

```
src/wiki_qa/
  __init__.py       # package marker
  cli.py            # argparse entry point; three modes (positional, --demo, REPL)
  agent.py          # Claude tool-use loop; returns AnswerResult
  wikipedia.py      # MediaWiki API client; search() returns lead-section extracts
  prompts.py        # SYSTEM_PROMPT and SEARCH_WIKIPEDIA_TOOL constants
  config.py         # MODEL and MAX_TOKENS
  __main__.py       # enables python -m wiki_qa
tests/
  test_wikipedia.py # wikipedia client unit tests (HTTP mocked)
  test_agent.py     # agent loop unit tests (Anthropic client mocked)
```

## Running tests

```bash
.venv/bin/python -m pytest tests/
```

## Model

Uses Claude Sonnet 4.5 via the Anthropic API.
