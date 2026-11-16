"""Deterministic final-report computation from stored evaluations (no LLM call)."""
from __future__ import annotations

from app.models import Answer, Question
from app.rubric import CRITERIA
from app.schemas import CriterionAverages, FinalSummary


def build_summary(questions: list[Question], answers: dict[int, Answer]) -> FinalSummary:
    answered = [answers[q.id] for q in questions if q.id in answers]
    if not answered:
        raise ValueError("no answers to summarise")

    avgs = {c: round(sum(getattr(a, c) for a in answered) / len(answered), 2) for c in CRITERIA}
    overall = round(sum(avgs.values()) / len(CRITERIA), 2)

    def ans_avg(a: Answer) -> float:
        return (a.relevance + a.structure + a.specificity) / 3

    ranked = sorted(answered, key=ans_avg)
    # Priority fixes: top_fix of the weakest answers, de-duplicated, max 3.
    fixes: list[str] = []
    for a in ranked:
        if a.top_fix not in fixes:
            fixes.append(a.top_fix)
        if len(fixes) == 3:
            break

    return FinalSummary(
        answered=len(answered),
        total_questions=len(questions),
        averages=CriterionAverages(**avgs),
        overall=overall,
        strongest_criterion=max(CRITERIA, key=lambda c: avgs[c]),
        weakest_criterion=min(CRITERIA, key=lambda c: avgs[c]),
        priority_fixes=fixes,
        best_question_id=ranked[-1].question_id,
        weakest_question_id=ranked[0].question_id,
    )
