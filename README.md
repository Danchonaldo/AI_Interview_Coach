# AI Interview Coach

Mock-interview practice for university students and junior applicants. Pick a role, language
and level, answer 6–8 interview questions in text, and get rubric-based AI scoring
(**Relevance**, **Structure (STAR)**, **Specificity**, 1–5) with personalised feedback, an
improved answer and the single most important fix. Finish to get a summary report; past
interviews are saved in a history view.

> Status (2026-11-16 checkpoint): first working version. The full flow is verified in **mock
> mode**. Real-AI mode (Anthropic/OpenAI) is implemented but **not yet verified live** because no
> API key was configured. See [CHECKPOINT_2026-11-16.md](CHECKPOINT_2026-11-16.md).

## Features implemented
- Role (Data Analyst / Marketing Intern / Python Developer), language (English / Russian), level (Intern / Junior), 6–8 questions
- AI question generation and AI answer grading, both through `backend/app/llm.py`, with strict JSON validation
- Evaluation card: three scores, feedback, improved answer, top fix
- Finish interview → summary (criterion averages, overall, strongest/weakest criterion, priority fixes)
- SQLite persistence and interview history
- Mock provider for offline, repeatable development and tests (clearly labelled in API and UI)

## Tech stack
React 19 · Vite 8 · Tailwind CSS 4 · Python 3.11+ (tested on 3.13) · FastAPI · SQLModel/SQLite · Pydantic v2 · pytest · Playwright (optional UI smoke test)

## Prerequisites
- Python 3.11+ and Node.js 20+ (tested with Node 22)
- For real AI: an Anthropic **or** OpenAI API key

## Backend setup
```bash
cd backend
python -m venv .venv
# macOS/Linux:  source .venv/bin/activate
# Windows:      .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # Windows: copy .env.example .env
```

### Environment variables (`backend/.env`, git-ignored)
| variable | meaning |
|---|---|
| `LLM_PROVIDER` | `mock` (default), `anthropic` or `openai` |
| `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL` | for `anthropic` |
| `OPENAI_API_KEY`, `OPENAI_MODEL` | for `openai` |
| `DATABASE_URL` | optional; default `sqlite:///backend/data/interview_coach.db` |
| `CORS_ORIGINS` | default `http://localhost:5173,http://127.0.0.1:5173` |

Keys live only on the backend. Never commit `.env`.

### Database
No manual step: tables are created automatically on backend start in `backend/data/interview_coach.db`.
Delete that file to reset local data.

### Run
```bash
cd backend
uvicorn app.main:app --reload --port 8000
# check: http://127.0.0.1:8000/health   API docs: http://127.0.0.1:8000/docs
```

## Frontend setup
```bash
cd frontend
npm install
npm run dev        # http://localhost:5173  (proxies /api -> http://127.0.0.1:8000)
```

## Using the MVP
1. Open http://localhost:5173. The header shows `MOCK MODE — not real AI` or `AI: anthropic/openai`.
2. Choose role, language, level and number of questions → **Start interview**.
3. Type an answer → **Submit answer** → read the evaluation card. Use **Next question →** or the numbered buttons.
4. **Finish interview** (enabled after ≥ 1 answer) → summary report.
5. **History** shows saved interviews; **Open** reopens one.

## API
| method | path | purpose |
|---|---|---|
| GET | `/health` | provider status (`is_mock`, `llm_ready`) |
| POST | `/sessions` | `{role, language, level, num_questions}` → session with generated questions |
| GET | `/sessions` | history |
| GET | `/sessions/{id}` | session with questions, answers, evaluations, summary |
| POST | `/questions/{id}/answers` | `{text}` → evaluation (re-submitting replaces the attempt) |
| POST | `/sessions/{id}/finish` | finish and compute summary (idempotent) |

Errors: 404 unknown id · 409 answering a finished session · 400 finishing with no answers ·
422 invalid input · 502 LLM failure / invalid LLM output · 503 provider not configured.

## Tests
```bash
cd backend && python -m pytest -q          # API flow, validation, persistence, LLM parsing (mock / fake providers)
cd .. && python -m pytest eval -q          # evaluation metric tests
cd frontend && npm run build               # frontend compiles
# optional UI smoke test (needs both servers running and `pip install playwright`):
python scripts/ui_smoke.py
```

## Real AI vs mock mode
- **Real mode** (`LLM_PROVIDER=anthropic|openai` + key): questions are generated and answers graded
  by the LLM with the rubric in `backend/app/rubric.py`. Output is validated; invalid output is
  retried once, then the API returns 502. There is no silent fallback to mock.
- **Mock mode** (default): deterministic heuristics (keyword/STAR/number detection) and a static
  question bank. It exists for tests and offline demos. **It is not AI**, every mock output is
  labelled, and mock results are never evidence of AI quality.

## AI evaluation
See [eval/README.md](eval/README.md): rubric, human-label dataset format, metrics
(target: all criteria within ±1 of human ratings on ≥ 80% of answers; stable repeated scores),
and the `eval/run_eval.py` harness. **No evaluation has been run yet.**

## Known limitations
- Live AI not verified yet (no API key during the checkpoint).
- No authentication — local single-user demo only; do not deploy publicly as-is.
- UI labels are English only; questions and feedback follow the selected language.
- Only the latest attempt per question is stored.

## Project docs
[PLAN.md](PLAN.md) · [DECISIONS.md](DECISIONS.md) · [CLAUDE.md](CLAUDE.md) / [AGENTS.md](AGENTS.md) ·
[agent-logs/](agent-logs/) · [CHECKPOINT_2026-11-16.md](CHECKPOINT_2026-11-16.md)
