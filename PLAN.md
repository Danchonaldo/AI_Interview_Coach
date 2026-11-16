# PLAN — AI Interview Coach

> **Provenance:** this plan was written on **2026-11-16** in the same Claude Code session that
> built the first version of the code (the GitHub repository was empty before that). It was not
> written before development started; it records the plan as reconstructed and agreed on the
> checkpoint day and will be updated as the project evolves.

## 1. Problem statement
Students and junior applicants rarely get realistic interview practice with honest, specific
feedback. Generic chatbots answer questions; they don't run a structured interview or grade
answers consistently. AI Interview Coach runs a role-specific mock interview and grades every
answer against a fixed STAR-based rubric with actionable coaching.

## 2. Target users
University students and junior job applicants (intern / junior level), English or Russian.

## 3. Core functionality
- Choose role (Data Analyst, Marketing Intern, Python Developer), language (EN/RU), level (Intern/Junior).
- Start an interview of 6–8 generated questions; answer in text.
- AI scores each answer 1–5 on Relevance, Structure (STAR), Specificity; shows feedback,
  an improved answer and the single most important fix.
- Finish → summary report (averages, strongest/weakest criterion, priority fixes).
- Completed interviews are saved; history view.

## 4. AI feature and evaluation approach
Two separate LLM capabilities behind one module (`backend/app/llm.py`):
1. **Question generation** — role/level/language-specific, category mix (behavioral, technical, situational, motivation), validated JSON.
2. **Answer grading** — fixed rubric (`backend/app/rubric.py`), strict JSON validated by Pydantic (integer scores 1–5, all fields required), one corrective retry, no silent fallback.

Evaluation (see `eval/README.md`): ~60 human-rated answers; targets — all three criteria within
±1 of humans on ≥ 80% of answers; stable scores across repeated runs; job-relevant questions and
useful feedback rated by the team.

## 5. MVP requirements (Nov 16 checkpoint)
- End-to-end flow: role → start → answer → evaluation → finish → summary; history.
- REST API: `POST /sessions`, `GET /sessions/{id}`, `POST /questions/{id}/answers`, `POST /sessions/{id}/finish`, `GET /sessions`.
- SQLite persistence; Pydantic validation; clear errors (404/409/422/502/503).
- Real provider support (Anthropic / OpenAI) + clearly labelled offline mock.
- Automated tests; README; PLAN; CLAUDE.md/AGENTS.md; DECISIONS; agent logs.

## 6. Stretch goals
- Voice answers (speech-to-text); follow-up questions based on the previous answer.
- Progress chart across interviews; export report to PDF.
- More roles; custom job description → tailored questions.
- Prompt-injection hardening tests; response caching.

## 7. Technology stack
React 19 + Vite 8 + Tailwind CSS 4 · Python 3.13 + FastAPI · SQLite + SQLModel · Pydantic v2 ·
Anthropic / OpenAI SDKs behind `llm.py` · pytest · Playwright (UI smoke test).

## 8. High-level architecture
```
Browser (React, :5173) --/api proxy--> FastAPI (:8000) --> llm.py --> provider (anthropic | openai | mock)
                                             |
                                             +--> SQLite (sessions, questions, answers + scores)
```
Summary statistics are computed deterministically from stored scores (no extra LLM call).

## 9. Milestones
| date | milestone |
|---|---|
| Nov 16 | Checkpoint: working MVP (mock + real-provider code), docs, first agent log, commit |
| Nov 23 | Real-provider verification with a team API key; prompt tuning; collect first 20 labelled answers |
| Nov 30 | 60 labelled answers; first evaluation run; fix weak criteria |
| Dec 7 | UX polish, stretch goal(s), second evaluation run, more agent sessions logged |
| **Dec 13** | **Code freeze**: REFLECTION.md, completed evaluation, final docs |

## 10. Team responsibilities
| member | responsibility |
|---|---|
| Daniyar Kekilbayev (@Danchonaldo) | repository owner, backend & integration |
| [Member 2 — name] | frontend / UX |
| [Member 3 — name] | AI prompts & evaluation dataset |
| [Member 4 — name] | testing, documentation, demo |
(Placeholders to be replaced with real names; every member must make meaningful commits.)

## 11. External dependencies
LLM API (Anthropic or OpenAI) and a key held by the team; npm and PyPI packages; GitHub.

## 12. Known risks
- No API key yet → live AI unverified (mitigation: mock mode for dev/tests, key this week).
- LLM output invalid / inconsistent → strict validation, retry, temperature 0, stability metric.
- Grader leniency / bias vs humans → evaluation against human labels; rubric anchors.
- Prompt injection inside answers → answer delimited and treated as data; tests planned.
- Cost / rate limits → small question count, no extra summary call.
- No authentication → local single-user demo only; must not be deployed publicly as-is.

## 13. November 16 checkpoint deliverables
Working MVP · PLAN.md · CLAUDE.md (+ AGENTS.md) · agent-logs/ with a genuine first session ·
README.md · DECISIONS.md · tests · eval framework · CHECKPOINT_2026-11-16.md · GitHub commit link.

## 14. December 13 code-freeze deliverables
Verified real-AI flow · completed evaluation with human labels and report · REFLECTION.md ·
3–5 significant agent sessions in agent-logs/ · production-quality README/DECISIONS ·
meaningful commits from every member.
