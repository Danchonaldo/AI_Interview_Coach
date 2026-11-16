# AI evaluation framework

Status on 2026-11-16: **framework ready, evaluation NOT yet run.** No human-labelled
dataset exists yet and no real LLM key was configured during the checkpoint session.
No evaluation results are claimed anywhere in this repository.

## What is evaluated

1. **Grader agreement** — do AI rubric scores match human ratings?
2. **Grader stability** — does the same answer get the same scores on repeated runs?
3. **Question quality** — are generated questions job-relevant? (human review, see below)
4. **Feedback usefulness** — is the feedback / improved answer / top fix actionable? (human review)

## Rubric

The single source of truth is [`backend/app/rubric.py`](../backend/app/rubric.py). It is
inserted verbatim into the grader prompt and is what human raters must use.
Three criteria, integer 1–5 each: **Relevance**, **Structure (STAR)**, **Specificity**.

## Dataset format (`eval/data/human_labels.jsonl`, to be created)

One JSON object per line:

| field | type | notes |
|---|---|---|
| `id` | string | unique |
| `role` | `data_analyst` \| `marketing_intern` \| `python_developer` | |
| `language` | `en` \| `ru` | |
| `level` | `intern` \| `junior` | |
| `question` | string | interview question |
| `answer` | string | candidate answer (real or written by team members; no personal data) |
| `human` | `{relevance, structure, specificity}` | ints 1–5; if several raters, the rounded median |
| `rater` | string | rater id(s), e.g. `"R1,R2"` |
| `notes` | string | optional |

See [`data/format_example.jsonl`](data/format_example.jsonl) — its scores are placeholder
zeros and are **rejected** by the harness on purpose; it shows the shape only.

### Collection protocol (planned)

- Target ~60 answers: 3 roles × 2 languages × ~10, spread across weak / medium / strong answers.
- At least 2 team members rate each answer independently with the rubric, without seeing AI scores.
- Record inter-rater agreement first; discuss and resolve disagreements > 1 point.

## Metrics (`eval/metrics.py`)

| metric | definition | target |
|---|---|---|
| all-criteria within ±1 | share of answers where every criterion is within ±1 of the human score | **≥ 80%** |
| per-criterion within ±1, exact, MAE, bias | per criterion | reported |
| stability | share of answers whose repeated scores spread ≤ 1 (and identical share) | ≥ 95% |

Question relevance and feedback usefulness: each team member rates 20 generated questions
(job-relevant yes/no) and 20 feedback cards (useful 1–5); report the averages.

## Running

```bash
# from the repo root, with the backend virtualenv active
python -m pytest eval -q                                     # metric unit tests
python eval/run_eval.py --data eval/data/human_labels.jsonl --provider anthropic --repeats 3
```

Outputs go to `eval/runs/` (git-ignored). Copy the final report to `eval/results/`.
`--provider mock` only proves the pipeline runs; its numbers are meaningless as AI quality.
