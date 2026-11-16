"""Reproducible grader evaluation: AI rubric scores vs human ratings.

Usage (from repo root, backend venv active):
    python eval/run_eval.py --data eval/data/human_labels.jsonl --provider anthropic --repeats 3

Writes eval/runs/<timestamp>_<provider>/{results.jsonl,report.json,report.md}.
eval/runs/ is git-ignored; copy a curated report into eval/results/ when it is final.

IMPORTANT: --provider mock only checks that the pipeline runs. Mock numbers say
nothing about AI quality and must never be reported as evaluation results.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "eval"))

from app.llm import get_provider  # noqa: E402
from metrics import CRITERIA, agreement, all_criteria_within_1, stability  # noqa: E402

REQUIRED = {"id", "role", "language", "level", "question", "answer", "human"}


def load(path: Path) -> list[dict]:
    rows = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        missing = REQUIRED - row.keys()
        if missing:
            raise SystemExit(f"{path}:{i}: missing fields {sorted(missing)}")
        for c in CRITERIA:
            v = row["human"].get(c)
            if not isinstance(v, int) or not 1 <= v <= 5:
                raise SystemExit(f"{path}:{i}: human.{c} must be an int 1-5")
        rows.append(row)
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, required=True)
    ap.add_argument("--provider", default=None, help="mock | anthropic | openai (default: LLM_PROVIDER)")
    ap.add_argument("--repeats", type=int, default=3, help="evaluations per answer (stability)")
    ap.add_argument("--out", type=Path, default=ROOT / "eval" / "runs")
    args = ap.parse_args()

    rows = load(args.data)
    provider = get_provider(args.provider)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = args.out / f"{stamp}_{provider.name}"
    out.mkdir(parents=True, exist_ok=True)

    items, failures = [], []
    for row in rows:
        runs = []
        for _ in range(args.repeats):
            try:
                ev = provider.evaluate_answer(row["role"], row["language"], row["level"], row["question"], row["answer"])
                runs.append(ev.model_dump())
            except Exception as e:  # record, keep going
                failures.append({"id": row["id"], "error": str(e)[:300]})
        if runs:
            items.append({"id": row["id"], "human": row["human"], "ai": runs[0], "runs": runs})
        print(f"{row['id']}: {len(runs)}/{args.repeats} ok", flush=True)

    with (out / "results.jsonl").open("w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")

    report = {
        "provider": provider.name,
        "is_mock": provider.is_mock,
        "dataset": str(args.data),
        "n_items": len(rows),
        "n_evaluated": len(items),
        "repeats": args.repeats,
        "failures": failures,
        "all_criteria_within_1": all_criteria_within_1(items),
        "per_criterion": {
            c: {
                "agreement": agreement([(it["ai"][c], it["human"][c]) for it in items]),
                "stability": stability([[r[c] for r in it["runs"]] for it in items]),
            }
            for c in CRITERIA
        },
        "targets": {"all_criteria_within_1": ">= 0.80", "stability.max_spread_le_1": ">= 0.95"},
    }
    (out / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        f"# Grader evaluation — {provider.name} — {stamp}",
        "",
        "> MOCK RUN: pipeline check only, NOT an AI quality result." if provider.is_mock else "",
        f"Items: {len(items)}/{len(rows)} · repeats: {args.repeats} · failures: {len(failures)}",
        f"All criteria within ±1 of human: **{report['all_criteria_within_1']}** (target ≥ 0.80)",
        "",
        "| Criterion | within ±1 | exact | MAE | bias | stability (spread ≤1) |",
        "|---|---|---|---|---|---|",
    ]
    for c in CRITERIA:
        a, s = report["per_criterion"][c]["agreement"], report["per_criterion"][c]["stability"]
        lines.append(f"| {c} | {a['within_1']} | {a['exact']} | {a['mae']} | {a['bias']} | {s['max_spread_le_1']} |")
    (out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nwritten to {out}")


if __name__ == "__main__":
    main()
