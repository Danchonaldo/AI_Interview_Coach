# TASK: Complete the November 16, 2026 Final Project Checkpoint

You are the lead implementation engineer for our university final project, **AI Interview Coach**.

**Your objective: Complete the entire November 16 Checkpoint in this single working session.**

Do not stop after planning or creating documentation. Inspect the existing repository, implement whatever is missing for the Checkpoint, run tests, verify the complete application, prepare the required documentation, and publish a verified GitHub commit when safe.

Work autonomously through the stages below. Do not ask for confirmation between routine stages. Stop only for genuine blockers, security risks, irreversible operations, or missing external permissions.

## 1. Project context

AI Interview Coach is a web application that helps students prepare for job interviews.

Target users: university students and junior job applicants.

Core functionality:

- Select a job role: Data Analyst, Marketing Intern, or Python Developer.
- Select interview language: English or Russian.
- Select experience level: Intern or Junior.
- Start an interview containing 6-8 questions.
- Submit answers as text.
- Evaluate answers using AI.
- Score answers from 1 to 5 using three criteria:
  - Relevance
  - Structure (STAR)
  - Specificity
- Display personalized feedback, an improved answer, and the most important improvement.
- Finish the interview and display a summary report.
- Save completed interviews and display their history.

The AI functionality must be substantive, not merely a generic ChatGPT chat interface.

Suggested stack, unless the existing repository already uses a working alternative:

- Frontend: React + Vite + Tailwind CSS
- Backend: Python + FastAPI
- Database: SQLite with SQLModel or SQLAlchemy
- AI integration: provider SDK through a single `llm.py` abstraction
- Validation: Pydantic
- Tests: pytest

Do not replace working technologies unnecessarily.

## 2. Mandatory university Checkpoint requirements

Deadline: **Monday, November 16, 2026**.

The Checkpoint is PASS/FAIL.

The exact minimum requirements are:

1. A first version of the product works end to end, even if rough.
2. `PLAN.md` exists.
3. `AGENTS.md` or `CLAUDE.md` exists.
4. First genuine agent logs exist inside `agent-logs/`.
5. The submission is a link to a real GitHub commit.

Additional project requirements that must guide implementation:

- Use an actual agentic coding tool.
- Implement a meaningful AI feature.
- Plan a reproducible AI evaluation.
- Never commit secrets.
- Keep meaningful Git contributions from group members.
- Maintain `README.md`, `DECISIONS.md`, tests, and an AI evaluation framework.
- `REFLECTION.md`, completed evaluation, and final production-quality documentation are required by the December 13 code freeze, not necessarily today's checkpoint.

Do not confuse today's Checkpoint with the final submission.

## 3. Stage A - Inspect the actual repository

Start with a READ-ONLY audit.

Inspect:

- Current working directory and repository root.
- Git status, current branch, remotes, and recent commits.
- Existing project architecture.
- Backend and frontend implementation.
- Database models.
- API routes.
- AI provider integration.
- Existing tests.
- README and documentation.
- Existing agent logs.
- Environment configuration.
- Any uncommitted changes.

Determine what already works and what remains missing.

Use three evidence categories:

- PROVEN - directly verified.
- LIKELY - supported by evidence but not tested.
- UNKNOWN - insufficient evidence.

Do not assume the repository is empty.

If implementation already exists, extend it safely.

If the intended project directory is empty, create the minimum project structure there.

If the current directory contains an unrelated repository or another project's files, STOP instead of modifying it.

Preserve unrelated and uncommitted changes.

## 4. Stage B - Create or update the project plan

Create or update `PLAN.md`.

It must contain:

1. Project name and problem statement.
2. Target users.
3. Core functionality.
4. AI feature and evaluation approach.
5. MVP requirements.
6. Stretch goals.
7. Technology stack.
8. High-level architecture.
9. Development milestones.
10. Team responsibilities, using placeholders if actual names are unknown.
11. External dependencies.
12. Known risks.
13. November 16 Checkpoint deliverables.
14. December 13 code-freeze deliverables.

If implementation has already started, honestly identify the plan as updated or reconstructed on November 16. Never falsely claim it was written before earlier development.

## 5. Stage C - Implement the minimum working Checkpoint

Our priority is a complete, demonstrable user journey.

Required flow:

**Choose role → Start interview → Answer questions → Receive evaluation → Finish interview → View summary.**

Prefer the smallest complete implementation.

### Backend

Implement or repair the necessary API routes:

- `POST /sessions`
- `GET /sessions/{id}`
- `POST /questions/{id}/answers`
- `POST /sessions/{id}/finish`

Add history retrieval if achievable without compromising the core flow.

Use SQLite for local persistence.

Ensure appropriate validation and error handling.

### AI integration

Centralize provider calls inside `llm.py`.

Implement two logically separate capabilities:

1. Interview question generation.
2. Answer evaluation using the predefined rubric.

The grader should return validated structured output containing:

- relevance score
- structure score
- specificity score
- feedback
- improved answer
- top fix

Validate all scores and structured responses.

Use an existing, configured real LLM provider when available.

For reliable local development, support a clearly labeled mock provider.

**Important:** Mock output is only a testing fallback. Never claim that mock responses prove real AI functionality.

Never generate or invent API credentials.

Never print actual secret values.

If a real provider is unavailable, finish the locally testable flow and clearly report that live AI verification remains blocked.

### Frontend

Create or finish:

1. Role and language selection.
2. Interview question interface.
3. Text answer submission.
4. Evaluation card.
5. Final results screen.

A simple, functional interface is sufficient.

Avoid unnecessary animations, advanced authentication, complex dashboards, and unrelated features.

### Security

- API keys only in backend environment variables.
- `.env` excluded from Git.
- `.env.example` contains placeholders only.
- No credentials embedded in frontend code.
- Do not expose user records through insecure authentication shortcuts.
- A local single-user demonstration mode is preferable to pretending an email-only form provides secure authentication.

## 6. Stage D - Create mandatory agent documentation

Create or update `CLAUDE.md` or `AGENTS.md` with:

- Project purpose.
- Architecture overview.
- Coding conventions.
- Directory responsibilities.
- How to run tests.
- How AI calls are managed.
- Security rules.
- Instructions to preserve working functionality.
- Restrictions on production, destructive commands, and unrelated refactors.

Create or update `DECISIONS.md`.

Document genuine engineering decisions:

- Which stack was selected and why.
- Which AI provider strategy was selected.
- How the evaluation rubric works.
- What trade-offs were made for the Checkpoint.
- Any agent mistakes and how they were detected, if they actually occurred.
- What remains deferred.

### Agent logs

Create or update:

`agent-logs/`

Preserve genuine records of this development session.

Use an available Claude Code session export or transcript when possible.

Logs must demonstrate:

- The task given to the agent.
- Actual implementation actions.
- Executed commands.
- Test results.
- Problems encountered.
- Corrections made.

Do not invent conversations, previous sessions, tool outputs, failures, or successful tests.

If historical sessions cannot be exported, report this explicitly and preserve genuine evidence from the current session.

Prepare a useful initial log. The final project should eventually contain 3-5 significant genuine sessions.

## 7. Stage E - README and evaluation foundation

Update `README.md` with:

- Project overview.
- Features currently implemented.
- Technology stack.
- Prerequisites.
- Backend installation commands.
- Frontend installation commands.
- Environment variable setup.
- Database initialization.
- Commands for running the application.
- How to use the MVP.
- How to execute tests.
- Known limitations.
- Real AI versus mock mode explanation.

The instructions must reflect the actual repository.

Prepare the AI evaluation foundation:

- An evaluation script or test harness appropriate to the implementation.
- A documented scoring rubric.
- A dataset format for human-labeled responses.
- Metrics for comparing AI scores to human ratings.

Target metrics for the final project:

- Agreement within ±1 point on at least 80% of evaluated answers.
- Stable scoring across repeated evaluations.
- Job-relevant generated questions.
- Useful feedback.

Do not fabricate a 60-answer dataset or evaluation results.

If time or resources are insufficient to collect genuine human ratings, document the pending evaluation honestly.

## 8. Stage F - Run verification

Actually execute all applicable checks.

At minimum:

1. Backend starts successfully.
2. Frontend starts successfully.
3. Database initializes correctly.
4. Session creation works.
5. Questions are returned.
6. Answer submission works.
7. Evaluation results satisfy the schema.
8. Session completion works.
9. Final results are returned.
10. Persistence works after a restart where applicable.
11. Relevant automated tests pass.

Verify the API using actual requests.

Where browser automation is available, open the application and test the real UI flow.

If browser automation is unavailable, report that limitation and verify the API and frontend build separately.

Test real LLM functionality if valid credentials are already configured.

Use mock mode for repeatable tests.

Inspect the final Git diff, not just test results.

Check for:

- Unexpected changes.
- Secrets.
- Broken imports.
- Generated files.
- Missing documentation.
- Unrelated modifications.
- Incorrect test claims.

Do not mark an unexecuted test as passed.

## 9. Stage G - Prepare the Checkpoint evidence

Create a concise file:

`CHECKPOINT_2026-11-16.md`

Include:

- Checkpoint date.
- Exact working MVP functionality.
- Components implemented.
- Verification commands and results.
- Real AI verification status.
- Mock verification status.
- Documentation completed.
- Known limitations.
- Missing requirements, if any.
- Demo instructions.
- Git branch and commit information.
- Next development priority.

This file is supplemental evidence, not a replacement for the required running application or GitHub commit.

Use verified statuses:

- CODE GREEN
- TESTS GREEN
- FUNCTIONAL GREEN
- NOT VERIFIED
- BLOCKED

Never claim GREEN without supporting evidence.

## 10. Stage H - Git commit and GitHub submission

The user authorizes you to prepare and publish **one focused Checkpoint commit** if all safety conditions are satisfied.

Before committing:

- Inspect `git status`.
- Review the final diff.
- Check for secrets.
- Confirm that unrelated changes are excluded.
- Stage only relevant files by explicit paths.

Do not use blind `git add .` or `git add -A`.

Do not overwrite or rewrite existing commits.

Do not force-push.

Do not modify protected branches.

If already working in a suitable project feature branch, use it.

Otherwise, create a dedicated branch:

`checkpoint/2026-11-16`

Create a descriptive commit, for example:

`feat: complete November 16 MVP checkpoint`

Push only the dedicated or clearly appropriate feature branch to the existing configured GitHub remote.

Do not create a public repository or change repository visibility without explicit permission.

If no remote exists or authentication fails, keep the verified local commit and provide the exact blocker and safe commands needed to publish it.

After pushing, verify the local HEAD and remote branch commit hashes match.

Return the **actual GitHub commit URL**.

Never invent a link or report PUSH GREEN before verification.

## 11. Final Checkpoint review

Before stopping, assess the university criteria one by one.

Use this checklist:

- [ ] First working end-to-end MVP.
- [ ] PLAN.md.
- [ ] AGENTS.md or CLAUDE.md.
- [ ] Genuine first agent logs.
- [ ] GitHub repository and real checkpoint commit.
- [ ] No committed secrets.
- [ ] Meaningful AI feature implemented.
- [ ] Verification evidence.
- [ ] README with actual setup instructions.
- [ ] Known remaining work documented.

Mark each item PASS, FAIL, or NOT VERIFIED based on evidence.

Check whether any mandatory Checkpoint requirement remains incomplete.

Do not declare the Checkpoint submission complete if the required commit link or working application is missing.

## 12. Final report to me

Respond in Russian.

Keep the final report concise and practical.

Provide:

**1. CHECKPOINT STATUS**

PASS / INCOMPLETE / BLOCKED, with a reason.

**2. IMPLEMENTED**

Exactly what now works.

**3. VERIFICATION**

Which tests and real application checks passed or failed.

**4. DOCUMENTATION**

Which required files exist.

**5. GIT**

Branch, commit hash, remote verification status, and GitHub commit URL.

**6. HOW TO DEMO**

Exact commands to launch and demonstrate the application.

**7. REMAINING BLOCKERS**

Only genuine missing requirements, external actions, or unresolved problems.

**8. WHAT I MUST SUBMIT**

Show the exact GitHub commit URL to paste into Canvas.

If something prevents completion, do as much safe work as possible and clearly distinguish finished work from remaining work.

---

**Execution instruction:**

Start now.

This is one complete Checkpoint execution task. Manage its internal stages independently, but verify each stage before proceeding. Do not stop after the audit, plan, or project skeleton.

Focus on meeting the real November 16 PASS/FAIL criteria, not implementing every feature planned for December 13.

Prefer a small, verified, genuinely functioning project over a large but broken implementation.

Do not fake success, tests, logs, evaluations, or GitHub evidence.