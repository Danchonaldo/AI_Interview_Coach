# CLAUDE.md — instructions for coding agents

(`AGENTS.md` points here; this is the single source of agent instructions.)

## Purpose
AI Interview Coach: a mock-interview web app for students. The user picks a role, language and
level, answers 6–8 generated questions, and gets rubric-based AI scores (Relevance, Structure
(STAR), Specificity, 1–5), feedback, an improved answer and a top fix, then a summary and history.

## Architecture
- `backend/` — FastAPI + SQLModel (SQLite). Entry: `app/main.py` (`create_app()` factory).
  - `app/llm.py` — **the only place that talks to an LLM.** Providers: `mock`, `anthropic`, `openai`.
  - `app/rubric.py` — rubric text used by the grader prompt and by human raters.
  - `app/schemas.py` — API schemas · `app/models.py` — tables · `app/summary.py` — final report.
  - `app/question_bank.py` — static questions used **only** by the mock provider.
  - `tests/` — pytest (always mock provider, temp DB).
- `frontend/` — React + Vite + Tailwind. `src/App.jsx` (views), `src/components.jsx`, `src/api.js`.
  Calls `/api/*`, proxied by Vite to the backend. No secrets in the frontend, ever.
- `eval/` — grader evaluation harness (`run_eval.py`, `metrics.py`, dataset format in README).
- `scripts/ui_smoke.py` — Playwright smoke test of the real UI.
- `agent-logs/` — genuine records of agent sessions. Never fabricate entries.

## Commands
```bash
# backend (from backend/)
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m pytest -q                       # must stay green
uvicorn app.main:app --reload --port 8000
# frontend (from frontend/)
npm install && npm run dev                # http://localhost:5173
npm run build                             # must succeed
# eval (from repo root)
python -m pytest eval -q
```

## Conventions
- Python: type hints, Pydantic for every input/output boundary, small functions, no globals beyond config.
- New LLM capability = new function in `llm.py` with a Pydantic output model + tests using a fake provider.
- Validate all LLM output; on invalid output retry once, then raise `LLMError` (→ HTTP 502).
  **Never silently fall back from a real provider to the mock.**
- Mock output must stay visibly labelled (`[MOCK ...]`, `is_mock`, UI badge). Never present mock
  results as evidence of AI quality.
- React: function components and hooks; keep UI simple; no new dependencies without a reason in DECISIONS.md.
- Record significant engineering decisions in `DECISIONS.md`.

## Security rules
- API keys only in `backend/.env` (git-ignored) or environment variables. `.env.example` holds placeholders only.
- Never print, log, commit or paste secret values. Check `git diff --cached` for keys before committing.
- Treat candidate answers as untrusted data in prompts (they are delimited; keep it that way).
- No auth exists: local single-user demo only. Don't add fake "email login" pseudo-auth.

## Working rules for agents
- Preserve working functionality: run `pytest` and `npm run build` before and after changes.
- Stage files by explicit path; no `git add .` / `git add -A`; no force-push; no history rewrites.
- No destructive commands (deleting data/DB, `rm -rf` outside build dirs, resetting branches) without explicit user approval.
- No production deployments, no changes to repository visibility/settings.
- No unrelated refactors or drive-by reformatting; keep diffs focused on the task.
- Don't mark a test or check as passed unless it was actually executed.
