"""SQLite tables (SQLModel)."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class InterviewSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    role: str
    language: str
    level: str
    status: str = "in_progress"  # in_progress | finished
    provider: str  # which LLM provider generated the questions (e.g. "mock", "anthropic")
    created_at: datetime = Field(default_factory=utcnow)
    finished_at: Optional[datetime] = None
    summary_json: Optional[str] = None  # stored FinalSummary, set on finish


class Question(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="interviewsession.id", index=True)
    position: int
    text: str
    category: str


class Answer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    question_id: int = Field(foreign_key="question.id", index=True, unique=True)
    text: str
    relevance: int
    structure: int
    specificity: int
    feedback: str
    improved_answer: str
    top_fix: str
    provider: str  # which LLM provider produced this evaluation
    created_at: datetime = Field(default_factory=utcnow)
