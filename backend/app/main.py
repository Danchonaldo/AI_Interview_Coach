"""FastAPI application: interview sessions, answers, evaluation, summary and history.

Local single-user demo mode: there is no authentication. Do not deploy publicly as-is.
"""
from __future__ import annotations

import logging
from typing import Callable, Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.engine import Engine
from sqlmodel import Session, select

from app.config import get_settings
from app.db import init_db, make_engine
from app.llm import LLMConfigError, LLMError, LLMProvider, get_provider
from app.models import Answer, InterviewSession, Question, utcnow
from app.schemas import (
    ROLE_LABELS,
    AnswerCreate,
    AnswerOut,
    EvaluationOut,
    FinalSummary,
    HealthOut,
    QuestionOut,
    SessionCreate,
    SessionListItem,
    SessionOut,
)
from app.summary import build_summary

log = logging.getLogger("interview_coach")


def _answer_out(a: Answer) -> AnswerOut:
    return AnswerOut(
        id=a.id,
        question_id=a.question_id,
        text=a.text,
        created_at=a.created_at,
        evaluation=EvaluationOut(
            relevance=a.relevance,
            structure=a.structure,
            specificity=a.specificity,
            average=round((a.relevance + a.structure + a.specificity) / 3, 2),
            feedback=a.feedback,
            improved_answer=a.improved_answer,
            top_fix=a.top_fix,
            provider=a.provider,
            is_mock=a.provider == "mock",
        ),
    )


def _load(db: Session, session_id: int):
    s = db.get(InterviewSession, session_id)
    if s is None:
        raise HTTPException(404, "session not found")
    questions = db.exec(
        select(Question).where(Question.session_id == session_id).order_by(Question.position)
    ).all()
    qids = [q.id for q in questions]
    answers = (
        {a.question_id: a for a in db.exec(select(Answer).where(Answer.question_id.in_(qids))).all()}
        if qids
        else {}
    )
    return s, questions, answers


def _session_out(db: Session, session_id: int) -> SessionOut:
    s, questions, answers = _load(db, session_id)
    return SessionOut(
        id=s.id,
        role=s.role,
        role_label=ROLE_LABELS[s.role][s.language],
        language=s.language,
        level=s.level,
        status=s.status,
        provider=s.provider,
        is_mock=s.provider == "mock",
        created_at=s.created_at,
        finished_at=s.finished_at,
        questions=[
            QuestionOut(
                id=q.id,
                position=q.position,
                text=q.text,
                category=q.category,
                answer=_answer_out(answers[q.id]) if q.id in answers else None,
            )
            for q in questions
        ],
        summary=FinalSummary.model_validate_json(s.summary_json) if s.summary_json else None,
    )


def create_app(
    database_url: Optional[str] = None,
    provider_factory: Callable[[], LLMProvider] = get_provider,
) -> FastAPI:
    settings = get_settings()
    engine: Engine = make_engine(database_url or settings.database_url)
    init_db(engine)

    app = FastAPI(title="AI Interview Coach API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )
    app.state.engine = engine

    def get_db():
        with Session(engine) as db:
            yield db

    def provider() -> LLMProvider:
        try:
            return provider_factory()
        except LLMConfigError as e:
            raise HTTPException(503, f"LLM provider not configured: {e}")

    @app.get("/health", response_model=HealthOut)
    def health():
        name = settings.llm_provider
        try:
            p = provider_factory()
            return HealthOut(status="ok", llm_provider=p.name, is_mock=p.is_mock, llm_ready=True)
        except LLMConfigError as e:
            return HealthOut(status="ok", llm_provider=name, is_mock=False, llm_ready=False, detail=str(e))

    @app.post("/sessions", response_model=SessionOut, status_code=201)
    def create_session(body: SessionCreate, db: Session = Depends(get_db), llm: LLMProvider = Depends(provider)):
        try:
            qs = llm.generate_questions(body.role, body.language, body.level, body.num_questions)
        except LLMError as e:
            log.warning("question generation failed: %s", e)
            raise HTTPException(502, f"question generation failed: {e}")
        s = InterviewSession(role=body.role, language=body.language, level=body.level, provider=llm.name)
        db.add(s)
        db.flush()
        for i, q in enumerate(qs.questions, start=1):
            db.add(Question(session_id=s.id, position=i, text=q.text, category=q.category))
        db.commit()
        return _session_out(db, s.id)

    @app.get("/sessions", response_model=list[SessionListItem])
    def list_sessions(db: Session = Depends(get_db)):
        out = []
        for s in db.exec(select(InterviewSession).order_by(InterviewSession.created_at.desc())).all():
            _, questions, answers = _load(db, s.id)
            summary = FinalSummary.model_validate_json(s.summary_json) if s.summary_json else None
            out.append(
                SessionListItem(
                    id=s.id, role=s.role, role_label=ROLE_LABELS[s.role][s.language],
                    language=s.language, level=s.level, status=s.status, provider=s.provider,
                    created_at=s.created_at, finished_at=s.finished_at,
                    answered=len(answers), total_questions=len(questions),
                    overall=summary.overall if summary else None,
                )
            )
        return out

    @app.get("/sessions/{session_id}", response_model=SessionOut)
    def get_session(session_id: int, db: Session = Depends(get_db)):
        return _session_out(db, session_id)

    @app.post("/questions/{question_id}/answers", response_model=AnswerOut, status_code=201)
    def submit_answer(
        question_id: int,
        body: AnswerCreate,
        db: Session = Depends(get_db),
        llm: LLMProvider = Depends(provider),
    ):
        q = db.get(Question, question_id)
        if q is None:
            raise HTTPException(404, "question not found")
        s = db.get(InterviewSession, q.session_id)
        if s.status == "finished":
            raise HTTPException(409, "session already finished")
        try:
            ev = llm.evaluate_answer(s.role, s.language, s.level, q.text, body.text)
        except LLMError as e:
            log.warning("evaluation failed: %s", e)
            raise HTTPException(502, f"evaluation failed: {e}")
        a = db.exec(select(Answer).where(Answer.question_id == question_id)).first()
        if a is None:
            a = Answer(question_id=question_id, text=body.text, provider=llm.name, **ev.model_dump())
        else:  # re-answering a question replaces the previous attempt
            a.text, a.provider, a.created_at = body.text, llm.name, utcnow()
            for k, v in ev.model_dump().items():
                setattr(a, k, v)
        db.add(a)
        db.commit()
        db.refresh(a)
        return _answer_out(a)

    @app.post("/sessions/{session_id}/finish", response_model=SessionOut)
    def finish_session(session_id: int, db: Session = Depends(get_db)):
        s, questions, answers = _load(db, session_id)
        if s.status == "finished":
            return _session_out(db, session_id)  # idempotent
        if not answers:
            raise HTTPException(400, "answer at least one question before finishing")
        summary = build_summary(questions, answers)
        s.status, s.finished_at, s.summary_json = "finished", utcnow(), summary.model_dump_json()
        db.add(s)
        db.commit()
        return _session_out(db, session_id)

    return app


app = create_app()
