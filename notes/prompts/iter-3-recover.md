Two changes to recover diagnostic data, then re-run.

In src/wiki_qa/agent.py, define a new exception:
pythonclass MaxTurnsExceeded(Exception):
    """Raised when the agent loop hits its turn limit. Carries partial state."""
    def __init__(self, partial: "AnswerResult"):
        super().__init__(f"Agent did not finish within {len(partial.messages)} turns.")
        self.partial = partial
Replace the raise RuntimeError(...) at the end of answer() with raise MaxTurnsExceeded(AnswerResult(answer="[did not converge]", searches=searches, messages=messages)). This way the partial state isn't lost.
In src/wiki_qa/evals/runner.py, update the try/except to handle MaxTurnsExceeded specifically:
pythontry:
    answer_result = agent.answer(case.question)
except agent.MaxTurnsExceeded as e:
    print(f"  WARN: max turns exceeded, using partial result")
    answer_result = e.partial
except Exception as e:
    print(f"  ERROR: {e}")
    answer_result = AnswerResult(answer=f"[agent error: {e}]", searches=[], messages=[])
This preserves search queries and partial messages even when the cap is hit, so we can grade and inspect them.
Run .venv/bin/python -m pytest tests/ -q to confirm nothing breaks. The test_max_turns_raises_on_runaway test will need to be updated to expect MaxTurnsExceeded instead of RuntimeError.
Re-run the v3 evals: .venv/bin/python -m wiki_qa.evals then cp results/latest.json results/v3_judge.json.
Show me the versailles_criticisms entry from the new v3 run: full searches list and the full answer text (which will be [did not converge] if cap was hit, but the searches list will be populated).