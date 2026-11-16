"""API request/response schemas (Pydantic)."""
from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

Role = Literal["data_analyst", "marketing_intern", "python_developer"]
Language = Literal["en", "ru"]
Level = Literal["intern", "junior"]

ROLE_LABELS: dict[str, dict[str, str]] = {
    "data_analyst": {"en": "Data Analyst", "ru": "Аналитик данных"},
    "marketing_intern": {"en": "Marketing Intern", "ru": "Стажёр по маркетингу"},
    "python_developer": {"en": "Python Developer", "ru": "Python-разработчик"},
}


class SessionCreate(BaseModel):
    role: Role
    language: Language = "en"
    level: Level = "intern"
    num_questions: int = Field(default=7, ge=6, le=8)


class AnswerCreate(BaseModel):
    text: str = Field(min_length=1, max_length=5000)

    @field_validator("text")
    @classmethod
    def not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("answer must not be blank")
        return v


class EvaluationOut(BaseModel):
    relevance: int
    structure: int
    specificity: int
    average: float
    feedback: str
    improved_answer: str
    top_fix: str
    provider: str
    is_mock: bool


class AnswerOut(BaseModel):
    id: int
    question_id: int
    text: str
    evaluation: EvaluationOut
    created_at: datetime


class QuestionOut(BaseModel):
    id: int
    position: int
    text: str
    category: str
    answer: Optional[AnswerOut] = None


class CriterionAverages(BaseModel):
    relevance: float
    structure: float
    specificity: float


class FinalSummary(BaseModel):
    answered: int
    total_questions: int
    averages: CriterionAverages
    overall: float
    strongest_criterion: str
    weakest_criterion: str
    priority_fixes: list[str]
    best_question_id: Optional[int] = None
    weakest_question_id: Optional[int] = None


class SessionOut(BaseModel):
    id: int
    role: str
    role_label: str
    language: str
    level: str
    status: str
    provider: str
    is_mock: bool
    created_at: datetime
    finished_at: Optional[datetime] = None
    questions: list[QuestionOut]
    summary: Optional[FinalSummary] = None


class SessionListItem(BaseModel):
    id: int
    role: str
    role_label: str
    language: str
    level: str
    status: str
    provider: str
    created_at: datetime
    finished_at: Optional[datetime] = None
    answered: int
    total_questions: int
    overall: Optional[float] = None


class HealthOut(BaseModel):
    status: str
    llm_provider: str
    is_mock: bool
    llm_ready: bool
    detail: Optional[str] = None
