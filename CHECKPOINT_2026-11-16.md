# Checkpoint evidence — 2026-11-16

Supplemental evidence for the November 16 PASS/FAIL checkpoint. It does not replace the running
application or the GitHub commit.

## Working MVP functionality (verified in mock mode)
Choose role (Data Analyst / Marketing Intern / Python Developer), language (EN/RU), level
(Intern/Junior), 6–8 questions → start interview → answer in text → evaluation card (Relevance,
Structure (STAR), Specificity 1–5, feedback, improved answer, top fix) → finish → summary report
→ saved history (persists across backend restarts).

## Components implemented
- Backend: FastAPI, `POST /sessions`, `GET /sessions`, `GET /sessions/{id}`, `POST /questions/{id}/answers`, `POST /sessions/{id}/finish`, `GET /health`; SQLite via SQLModel; Pydantic validation; error codes 400/404/409/422/502/503.
- AI layer `backend/app/llm.py`: question generation + rubric grading as separate capabilities; Anthropic and OpenAI providers; strict structured-output validation with one retry; labelled mock provider.
- Frontend: React + Vite + Tailwind — setup, interview, evaluation card, summary, history, mock/AI status badge.
- Tests: 22 backend tests, 3 eval-metric tests, Playwright UI smoke script.
- Eval foundation: rubric, dataset format, metrics, harness (`eval/`).

## Verification (commands actually executed in session 01)
| check | command | result | status |
|---|---|---|---|
| backend unit/API tests | `cd backend && python -m pytest -v` | 22 passed | TESTS GREEN |
| eval metric tests | `python -m pytest eval -v` | 3 passed | TESTS GREEN |
| frontend build | `cd frontend && npm run build` | built, no errors | CODE GREEN |
| backend starts, DB initialises | `uvicorn app.main:app` | startup complete, `backend/data/interview_coach.db` created | FUNCTIONAL GREEN |
| frontend starts, proxy works | `npx vite`; `curl :5173/api/health` | `{"status":"ok","llm_provider":"mock",...}` | FUNCTIONAL GREEN |
| create session / questions | `curl -X POST /sessions` | 201, 8 questions | FUNCTIONAL GREEN |
| answer + evaluation schema | `curl -X POST /questions/1/answers` | scores 1–5 + all text fields | FUNCTIONAL GREEN |
| finish + summary | `curl -X POST /sessions/1/finish` | `finished`, summary returned | FUNCTIONAL GREEN |
| error handling | 404 / 422 / 409 cases | as expected | FUNCTIONAL GREEN |
| persistence after restart | kill + restart uvicorn, `GET /sessions/1` | data intact | FUNCTIONAL GREEN |
| real UI flow in a browser | `python scripts/ui_smoke.py` (headless Chrome) | "UI SMOKE TEST PASSED", screenshots saved | FUNCTIONAL GREEN |
| real-provider config error path | `LLM_PROVIDER=anthropic`, no key | `/health llm_ready:false`, `POST /sessions` 503 | FUNCTIONAL GREEN |
| **live real-AI generation & grading** | — | no API key available | **BLOCKED** |
| AI evaluation vs human labels | — | dataset not collected yet | **NOT VERIFIED** (planned) |

Raw outputs: [`agent-logs/2026-11-16_session-01_evidence/`](agent-logs/2026-11-16_session-01_evidence/).

## Real AI verification status — BLOCKED
Real providers are implemented and their parsing/validation/retry path is unit-tested with a fake
provider, but no `ANTHROPIC_API_KEY`/`OPENAI_API_KEY` existed in the session, so no live LLM call
was made. To verify: put a key in `backend/.env`, set `LLM_PROVIDER=anthropic` (or `openai`),
restart the backend, run one interview; `/health` must show `"is_mock": false`.

## Mock verification status — GREEN
All functional checks above ran with `LLM_PROVIDER=mock`. Mock output is heuristic and labelled
`[MOCK …]`; it proves the application flow, **not** AI quality.

## Documentation completed
README.md · PLAN.md · CLAUDE.md · AGENTS.md · DECISIONS.md · eval/README.md · agent-logs/ (session 01) · this file.

## Known limitations
No live-AI verification yet · no human-labelled evaluation yet · no authentication (local
single-user demo) · English UI labels · only the latest attempt per question is stored.

## Missing requirements
None of the five mandatory checkpoint items is missing in the repository content. Real-AI
verification is outstanding and is the first priority below.

## Demo instructions
```bash
# terminal 1
cd backend && python -m venv .venv && .venv\Scripts\activate   # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt && copy .env.example .env      # macOS/Linux: cp
uvicorn app.main:app --port 8000
# terminal 2
cd frontend && npm install && npm run dev
# open http://localhost:5173 → Data Analyst / English / Intern → Start interview
# answer 2 questions (one strong STAR answer, one vague) → compare evaluation cards → Finish → History
```

## Git
- Branch: `checkpoint/2026-11-16` in `Danchonaldo/AI_Interview_Coach` (the repository had no commits before this one).
- Commit: the commit that adds this file — message `feat: complete November 16 MVP checkpoint`.
  Its hash and URL are reported in the agent's final report and visible on GitHub.

## Next development priority
1. Add a team API key and verify the real-AI flow end to end; tune prompts.
2. Collect human-labelled answers (target ~60) and run `eval/run_eval.py`.
3. Every team member makes meaningful commits; log 2–4 more significant agent sessions.
