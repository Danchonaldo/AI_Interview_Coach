"""Agreement / stability metrics for comparing AI scores with human ratings."""
from __future__ import annotations

from statistics import mean

CRITERIA = ("relevance", "structure", "specificity")


def agreement(pairs: list[tuple[int, int]]) -> dict:
    """pairs = [(ai_score, human_score), ...] for one criterion."""
    if not pairs:
        return {"n": 0, "within_1": None, "exact": None, "mae": None, "bias": None}
    diffs = [ai - h for ai, h in pairs]
    return {
        "n": len(pairs),
        "within_1": round(sum(abs(d) <= 1 for d in diffs) / len(diffs), 3),
        "exact": round(sum(d == 0 for d in diffs) / len(diffs), 3),
        "mae": round(mean(abs(d) for d in diffs), 3),
        "bias": round(mean(diffs), 3),  # >0: AI scores higher than humans
    }


def stability(runs: list[list[int]]) -> dict:
    """runs = per item, the list of scores from repeated evaluations of the SAME answer."""
    multi = [r for r in runs if len(r) >= 2]
    if not multi:
        return {"n": 0, "identical": None, "max_spread_le_1": None, "mean_spread": None}
    spreads = [max(r) - min(r) for r in multi]
    return {
        "n": len(multi),
        "identical": round(sum(s == 0 for s in spreads) / len(spreads), 3),
        "max_spread_le_1": round(sum(s <= 1 for s in spreads) / len(spreads), 3),
        "mean_spread": round(mean(spreads), 3),
    }


def all_criteria_within_1(items: list[dict]) -> float | None:
    """Share of answers where EVERY criterion is within +-1 of the human score (target >= 0.80)."""
    ok = [all(abs(it["ai"][c] - it["human"][c]) <= 1 for c in CRITERIA) for it in items]
    return round(sum(ok) / len(ok), 3) if ok else None
