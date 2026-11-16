# Agent session 01 — 2026-11-16 — Checkpoint MVP from an empty repository

- **Tool:** Claude (Claude Code–based agent harness in the Claude app), model Claude Opus 5.5
- **Operator:** Daniyar Kekilbayev (@Danchonaldo)
- **Time:** 2026-11-16, ~22:01–22:30 (UTC+5)
- **Working copy:** agent's cloud Linux workspace (`/home/claude/ai-interview-coach`), pushed to GitHub

## How this log was produced (read first)
No raw transcript file (e.g. a `.jsonl` session export) exists inside the agent's workspace, so
this log was written by the agent at the end of the session from its own tool history. **Every
command output quoted or linked below is the real captured output** (saved with `tee` while the
commands ran) — see `2026-11-16_session-01_evidence/`. Nothing was reconstructed from memory or
invented. The only edit to the captured files: one temporary output path in `eval_check.txt` was
shortened to `<tmp>`. To add the full conversation, export it from the Claude app and save it next to this file.

## Task given to the agent
Full prompt: [`2026-11-16_session-01_task-prompt.md`](2026-11-16_session-01_task-prompt.md).
Summary: complete the November 16 PASS/FAIL checkpoint in one session — audit the repo, write
PLAN.md, implement the minimal end-to-end MVP (role → start → answer → AI evaluation → finish →
summary), CLAUDE.md/AGENTS.md, DECISIONS.md, README, eval foundation, genuine agent logs, verify
everything, and publish one focused commit to GitHub. User message: «сделай».

## Timeline of actual actions

### 1. Read-only audit — the project did not exist yet
- Workspace: `/home/claude` was not a git repository; no project files.
- Checked tooling: Python 3.13, Node 22, git, gh present. `gh auth status` → *"The token in GH_TOKEN is invalid"*.
- Checked API keys **by presence only** (values never printed): `ANTHROPIC_API_KEY=unset`, `OPENAI_API_KEY=unset`, `GEMINI_API_KEY=unset`.
- Listed (names only) the user's computer folders (`PycharmProjects`, `IdeaProjects`, `Desktop`, `source/repos`, `frontendproj`…): no AI Interview Coach project. `frontendproj` contained an unrelated project → not touched.
- **Problem:** project location unknown → asked the user. Answer: «у меня есть гитхаб просто на сайте».
- User opened GitHub in the built-in browser and signed in; agent read the repository list and found `Danchonaldo/AI_Interview_Coach` (public).
- `git clone https://github.com/Danchonaldo/AI_Interview_Coach.git` → *"warning: You appear to have cloned an empty repository."* → **decision: build from scratch** (nothing to preserve).

### 2. Backend (FastAPI + SQLModel + SQLite)
- Created venv; `pip install fastapi sqlmodel uvicorn pytest httpx anthropic openai python-dotenv`.
- Wrote `backend/app/`: `config.py`, `models.py`, `db.py`, `schemas.py`, `rubric.py`, `question_bank.py`, `llm.py`, `summary.py`, `main.py`.
- `llm.py`: providers `mock` / `anthropic` / `openai`; JSON extraction; Pydantic validation; one corrective retry; `LLMError` → HTTP 502; `LLMConfigError` → HTTP 503; no silent fallback to mock.
- Tests `backend/tests/test_api.py`, `test_llm.py` (mock + a fake provider that exercises the real parsing/retry path).
- First run: `python -m pytest -q` → **22 passed** ([pytest_first_run.txt](2026-11-16_session-01_evidence/pytest_first_run.txt)).
- Small self-correction before running anything: simplified the question-count trimming logic in `_PromptedProvider.generate_questions` (the first version had a redundant conditional).

### 3. Frontend (React 19 + Vite 8 + Tailwind 4)
- `npm view` to get current versions, wrote `package.json`, `npm install` → *"added 35 packages"*.
- Wrote `src/App.jsx` (setup, interview, summary, history views), `src/components.jsx` (evaluation card, mock badge), `src/api.js`; Vite proxy `/api` → `:8000`.
- `npm run build` → built OK.
- Self-review fix: added `key={session.id}` to `<Interview>` so the current-question state resets when another session is opened from History.

### 4. Live verification with real requests
- Started `uvicorn app.main:app` (:8000, `LLM_PROVIDER=mock`) and `vite` (:5173) on a fresh DB.
- curl through the real HTTP API: health via the Vite proxy, create session (8 questions), answer, evaluation JSON, finish, history, error codes 404/422/409 → [api_check.txt](2026-11-16_session-01_evidence/api_check.txt).
- Killed and restarted the backend → session 1 still `finished` with its summary → [restart_check.txt](2026-11-16_session-01_evidence/restart_check.txt).
- Real-provider mode without a key (`LLM_PROVIDER=anthropic`) → `/health` reports `llm_ready:false`, `POST /sessions` → 503 with a clear message → [real_provider_check.txt](2026-11-16_session-01_evidence/real_provider_check.txt).
- **Live AI could not be tested: no API key is configured.** Nothing in this log claims real-AI quality.

### 5. Real UI flow in a browser
- The Claude desktop built-in browser cannot reach the agent workspace's localhost, so the UI was driven with headless Chrome via Playwright: `python scripts/ui_smoke.py` → setup → start → 2 answers → evaluation cards → finish → summary → history → *"UI SMOKE TEST PASSED"*, no page errors → [ui_smoke.txt](2026-11-16_session-01_evidence/ui_smoke.txt), [screenshots](2026-11-16_session-01_evidence/screenshots/).

### 6. Evaluation foundation
- `eval/metrics.py` (within ±1, exact, MAE, bias, stability, all-criteria-within-±1), `eval/run_eval.py`, `eval/README.md`, `eval/data/format_example.jsonl`.
- `pytest eval` → 3 passed. Harness correctly **rejects** the format example (placeholder 0 scores). Pipeline smoke run on a temporary copy with placeholder scores, mock provider → report produced and marked *"MOCK RUN: pipeline check only"* → [eval_check.txt](2026-11-16_session-01_evidence/eval_check.txt). **No evaluation results are claimed.**

### 7. Documentation
PLAN.md (marked as written on Nov 16 alongside the code), CLAUDE.md + AGENTS.md (pointer), DECISIONS.md, README.md, eval/README.md, CHECKPOINT_2026-11-16.md, this log.

### 8. Final checks before commit
- `pytest -v` → 22 passed; `pytest eval -v` → 3 passed; `npm run build` OK → [final_tests.txt](2026-11-16_session-01_evidence/final_tests.txt).
- Diff/secret review and the commit/push outcome are recorded in `CHECKPOINT_2026-11-16.md`.

## Problems encountered and how they were handled
| problem | handling |
|---|---|
| No project folder on the computer, none in the workspace | asked the user instead of guessing; found the GitHub repo via the browser |
| GitHub repo empty | built the MVP from scratch; documented in PLAN/DECISIONS |
| `gh` token invalid; GitHub not linked to Claude | user linked GitHub in claude.ai |
| Push refused: Claude GitHub App not installed on the repo | asked the user to install the app for `AI_Interview_Coach` (outcome: see CHECKPOINT file) |
| No LLM API key | implemented real providers + verified the "not configured" path; live AI marked BLOCKED |
| Built-in browser can't open the agent's localhost | used headless Chrome (Playwright) in the workspace for the UI flow |
