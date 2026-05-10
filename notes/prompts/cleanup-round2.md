Cleanup Round 2: HTTP timeout and CLI error handling
Two real fixes. Both address user-facing failure modes that currently surface as Python stack traces.
1. HTTP timeout on Wikipedia requests
In src/wiki_qa/wikipedia.py, add timeout=10 to the requests.get call. A hung Wikipedia request will now raise requests.exceptions.Timeout after 10 seconds rather than blocking forever.
Add a unit test in tests/test_wikipedia.py asserting the timeout is passed in the call. Use mock_get.call_args.kwargs.get("timeout") to check.
2. CLI error handling
In src/wiki_qa/cli.py, wrap calls to agent.answer() so that exceptions surface as clean error messages instead of stack traces. Specifically:

Catch requests.exceptions.RequestException (covers timeouts, HTTP errors, connection errors) and print: Error: Wikipedia request failed ({error}). Try again or check your connection. to stderr, exit code 1.
Catch anthropic.APIError (covers auth failures, rate limits, etc.) and print: Error: Anthropic API request failed ({error}). Check your ANTHROPIC_API_KEY. to stderr, exit code 1.
Catch generic Exception as a fallback and print: Error: {error} to stderr, exit code 1.

Apply this to all three modes: positional question, --demo, and the REPL. For the REPL, don't exit on error — print the message and loop back to the prompt so the user can try another question. For the other two modes, exit.
Don't add CLI tests — argparse glue isn't worth mocking. But do verify --help still works.
Verification

.venv/bin/python -m pytest tests/ -q — should be 28 passing now (27 + 1 new timeout test)
.venv/bin/python -m wiki_qa --help — confirm the help still renders

Show me the final diff and both verification outputs.