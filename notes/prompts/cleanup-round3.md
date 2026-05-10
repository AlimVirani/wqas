Reorganizing build artifacts for clarity.

Create a notes/ directory at the project root.
Move these files into notes/ using git mv (preserves history):

CLAUDE.md
PLAN.md
EVAL_NOTES.md


Move prompts/ → notes/prompts/ using git mv.
Create notes/README.md with this content:

markdown# Build artifacts

This directory contains files used during development that aren't part of the runtime system. They're preserved for transparency about how the project was built.

- `CLAUDE.md` — project conventions for Claude Code (the AI coding tool used during development).
- `PLAN.md` — original phased build plan: Phase 1 skeleton, Phase 2 eval suite, Phase 3 prompt iteration.
- `EVAL_NOTES.md` — observations captured from the Phase 1 demo run that informed Phase 2 eval design.
- `prompts/` — task prompts written for Claude Code at each build phase. Reading these in order shows how each phase was scoped.

Verify nothing in the source code references these files by relative path. Search: grep -r "EVAL_NOTES\|PLAN.md\|CLAUDE.md" src/ tests/ pyproject.toml — should find nothing.
Run tests to confirm nothing breaks: .venv/bin/python -m pytest tests/ -q

Show me the new directory tree (ls -la of root and ls notes/) and the test output. Don't commit yet.