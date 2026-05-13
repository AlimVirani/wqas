Trim results/README.md
The current results/README.md is too long and duplicates content that belongs in the rationale doc. Trim it to the parts that are uniquely useful for a reviewer reading the results files: file legend, JSON structure reference, and headline baseline numbers.
Remove these sections entirely:

"Iteration timeline" — belongs in the rationale doc, not here
"Where the interesting data is" — belongs in the rationale doc
"Reproducing the baseline" — the main README.md already covers this

Keep these sections:

Brief overview (1-2 sentences)
File naming convention (the legend table)
JSON structure (per-case fields, retrieved structure, grades structure)
Current baseline section, trimmed to just: case counts, bucket breakdown, and pass-rate table. Drop the "where the interesting data is" subsection.
Graders — keep but trim each to one sentence. The detail (LLM-judge classifications, source paths) is for someone who needs to dig in; keep enough that they can.

Target length: ~50-60 lines of markdown. Currently ~140. Cut aggressively.
Tone: stay reference-flavored. No narrative. No "the system gracefully handles" language.
After trimming, show me the full new file inline so I can review before saving.