# results/

Eval-suite outputs across prompt versions, grader configurations, and suite generations. Current canonical baseline: `v2_33cases.json`.

---

## Files

Three naming axes: prompt version (`v0`/`v1`/`v2`), grader type (`substring` = phrase-match honest_failure, no suffix = LLM-judge), suite generation (no suffix = 13 cases).

| File | Cases | Notes |
|---|---|---|
| `v0_substring.json` | 13 | v0 prompt, substring honest_failure |
| `v0_judge.json` | 13 | v0 prompt, LLM-judge honest_failure |
| `v1_substring.json` | 13 | v1 prompt, substring honest_failure |
| `v1_judge.json` | 13 | v1 prompt, LLM-judge honest_failure |
| `v2_substring.json` | 13 | v2 prompt, substring honest_failure |
| `v2_judge.json` | 13 | v2 prompt, LLM-judge honest_failure |
| `v2_24cases.json` | 24 | v2 prompt, 4 graders (faithfulness added) |
| `v2_33cases.json` | 33 | **Current canonical baseline** |

`latest.json` is written by every run and is gitignored.

---

## JSON structure

Each file is a JSON array, one object per case.

**Top-level fields:**

| Field | Type | Description |
|---|---|---|
| `id` | string | Case identifier |
| `question` | string | Question posed to the agent |
| `category` | string | Failure-mode category (`simple_factual`, `multi_hop`, `adversarial`, …) |
| `expected_facts` | list[str] | Substrings expected in the answer |
| `expected_abstention` | bool | Whether the agent should abstain |
| `min_searches` / `max_searches` | int / int\|null | Search count bounds |
| `notes` | string | Case design rationale |
| `answer` | string | Agent's final answer |
| `searches` | list[str] | Queries issued, in order |
| `retrieved` | list[list[{title, extract}]] | Wikipedia results per query, parallel to `searches` |
| `grades` | object | See below |

**`grades` structure:**
```json
{
  "fact_recall":     {"applicable": true, "passed": true, "matched": [...], "missing": []},
  "search_behavior": {"passed": true, "actual": 2, "expected_min": 1, "expected_max": null, "queries": [...]},
  "honest_failure":  {"applicable": false},
  "faithfulness":    {"applicable": true, "passed": true, "verdict": "fully_supported", "rationale": "..."}
}
```

`applicable: false` — grader does not apply to this case. A missing key — grader was not run (e.g. `--fast` mode).

---

## Current baseline (`v2_33cases.json`)

33 cases: 13 base / 6 product / 14 hard

| Bucket | Contents |
|---|---|
| `base` | Core factual, multi-hop, and known-fact cases |
| `product` | User-facing query patterns: ambiguous terms, comparisons, geography |
| `hard` | Adversarial inputs, safety probes, fake entities, lead-section-insufficient questions |

| Grader | Score |
|---|---|
| fact_recall | 25/26 (96%) |
| search_behavior | 30/33 (91%) |
| honest_failure | 7/7 (100%) |
| faithfulness | 24/30 (80%) |

---

## Graders

**`fact_recall`** — Unicode-normalized substring match of `expected_facts` against the answer; `applicable: false` for abstention cases.

**`search_behavior`** — checks `len(searches)` against `min_searches`/`max_searches`; `max_searches: 0` is used for safety cases that must not search at all.

**`honest_failure`** — LLM-as-judge; applicable only to abstention cases. Verdicts: `appropriate_abstention`, `appropriate_hedging`, `over_claimed`, `under_claimed`.

**`faithfulness`** — LLM-as-judge; applicable when the agent produced an answer with retrieved extracts. Verdicts: `fully_supported`, `partially_supported`, `unsupported`.
