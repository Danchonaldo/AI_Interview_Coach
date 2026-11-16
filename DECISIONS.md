# DECISIONS

Engineering decisions log. Newest at the bottom. Format: context → decision → trade-off.

## D1 — Stack (2026-11-16)
- **Context:** GitHub repo `Danchonaldo/AI_Interview_Coach` was empty; no existing stack to preserve.
- **Decision:** the course-suggested stack — React 19 + Vite 8 + Tailwind 4, FastAPI, SQLite + SQLModel, Pydantic v2, pytest.
- **Why:** FastAPI + Pydantic give request/response validation for free and match the need to validate LLM JSON; SQLite needs no server; Vite proxy keeps the API on one origin in dev.
- **Trade-off:** SQLite + no auth = single-user local demo only.

## D2 — LLM provider strategy (2026-11-16)
- **Decision:** one module `backend/app/llm.py` with a provider interface and three providers: `anthropic`, `openai`, `mock`; selected with `LLM_PROVIDER`.
- Real providers share one code path: prompt → text → JSON extraction (tolerates ```json fences) → Pydantic validation → **one corrective retry** with the validation error → `LLMError` (HTTP 502). Temperature 0 for grading stability.
- **No silent fallback** to mock when the real provider fails — a failed AI call must be visible, otherwise demos could pass off heuristic output as AI.
- The **mock** is a deterministic heuristic (STAR keyword detection, numbers, length). It exists so that tests and offline development are repeatable. All mock output is labelled `[MOCK …]`, the API returns `is_mock`, the UI shows a "MOCK MODE — not real AI" badge.
- **Trade-off:** two real SDKs to maintain; justified because the team has not yet decided which key it will use.

## D3 — Evaluation rubric (2026-11-16)
- Three criteria, integer 1–5, with written anchors for every level (`backend/app/rubric.py`): Relevance, Structure (STAR — for technical questions the equivalent context → approach → outcome flow), Specificity (own actions, tools, numbers).
- The same text is inserted into the grader prompt and given to human raters, so AI-vs-human agreement measures the model, not a rubric mismatch.
- Scores are strictly validated: floats like 3.5, booleans, 0 or 6 are rejected.
- The improved answer must keep the candidate's facts and use placeholders like `[number]` instead of inventing achievements.
- The candidate answer is delimited (`<<<ANSWER … ANSWER>>>`) and the system prompt says to ignore instructions inside it (basic prompt-injection mitigation; not yet tested against real models).

## D4 — Summary without an extra LLM call (2026-11-16)
- The final report (criterion averages, strongest/weakest criterion, top-3 priority fixes from the weakest answers) is computed deterministically from stored scores.
- **Why:** cheaper, instant, reproducible; avoids a third unvalidated AI output. An AI-written narrative summary is a possible stretch goal.

## D5 — Checkpoint trade-offs (2026-11-16)
- Re-answering a question replaces the previous attempt (simple practice loop; attempt history deferred).
- A session can be finished after ≥ 1 answer (partial interviews still produce a report).
- No authentication; "local single-user demo mode" instead of a fake email-only login.
- Schema created with `SQLModel.metadata.create_all` on startup; migrations (Alembic) deferred until the schema changes.
- UI text is English; questions/feedback follow the chosen interview language.

## D6 — Agent process notes (2026-11-16, factual)
- The agent (Claude Code, Claude Opus 5.5) first searched the user's computer and found no project folder, asked the user, then found the GitHub repository and confirmed by cloning that it had **no commits**. The project was therefore created from scratch rather than "extended".
- Pushing from the agent's cloud workspace initially failed because no GitHub account was linked to the agent (`add_repo: link your GitHub account…`); see the checkpoint file for how the commit was published.
- No incorrect code was committed during this session that later had to be reverted; all 22 backend tests passed on their first run. (Recorded so later sessions can compare.)

## Deferred (to Dec 13 or later)
- Live verification with a real API key (blocked: no key configured on Nov 16).
- Human-labelled dataset and the actual evaluation run.
- Prompt-injection tests against the real model; question-relevance and feedback-usefulness reviews.
- REFLECTION.md, deployment considerations, attempt history, migrations.
