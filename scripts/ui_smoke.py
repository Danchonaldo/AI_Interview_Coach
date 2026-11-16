"""Headless browser smoke test of the real UI flow.

Requires: backend on :8000 and `npm run dev` on :5173, and Python Playwright.
Usage:  python scripts/ui_smoke.py [--url http://127.0.0.1:5173] [--shots DIR]

Flow: choose role/language/level -> start -> answer 2 questions -> evaluation card
      -> finish -> summary -> history.
"""
from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

ANSWER = (
    "In my second-year course project the situation was that our team had no clean data. "
    "My task was to prepare it for analysis. I used pandas to remove duplicates and I wrote "
    "SQL queries to join three tables. As a result the report was ready 2 days early."
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:5173")
    ap.add_argument("--shots", default=None, help="directory for screenshots")
    args = ap.parse_args()
    shots = Path(args.shots) if args.shots else None
    if shots:
        shots.mkdir(parents=True, exist_ok=True)

    def shot(page, name):
        if shots:
            page.screenshot(path=str(shots / f"{name}.png"), full_page=True)

    chrome = os.getenv("CHROME_PATH") or shutil.which("google-chrome") or None
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=chrome) if chrome else p.chromium.launch()
        page = browser.new_page(viewport={"width": 1000, "height": 900})
        errors: list[str] = []
        page.on("pageerror", lambda e: errors.append(str(e)))

        page.goto(args.url)
        expect(page.get_by_text("Set up your interview")).to_be_visible()
        page.get_by_role("button", name="Data Analyst").click()
        page.get_by_role("button", name="English").click()
        page.get_by_role("button", name="Junior").click()
        page.get_by_label("Questions").select_option("6")
        shot(page, "1_setup")
        page.get_by_role("button", name="Start interview").click()

        expect(page.get_by_text("Question 1 of 6")).to_be_visible(timeout=60_000)
        print("question 1:", page.get_by_test_id("question-text").inner_text())
        page.get_by_role("textbox").fill(ANSWER)
        page.get_by_role("button", name="Submit answer").click()
        expect(page.get_by_text("Most important fix")).to_be_visible(timeout=60_000)
        scores = {c: page.get_by_test_id(f"score-{c}").inner_text() for c in ("Relevance", "Structure (STAR)", "Specificity")}
        print("evaluation scores q1:", scores)
        shot(page, "2_evaluation")

        page.get_by_role("button", name="Next question →").click()
        expect(page.get_by_text("Question 2 of 6")).to_be_visible()
        page.get_by_role("textbox").fill("I am good with data.")
        page.get_by_role("button", name="Submit answer").click()
        expect(page.get_by_text("Most important fix")).to_be_visible(timeout=60_000)
        print("answered: ", page.get_by_text("answered").first.inner_text())

        page.get_by_role("button", name="Finish interview").click()
        expect(page.get_by_text("Interview summary")).to_be_visible(timeout=30_000)
        print("overall score:", page.get_by_test_id("overall-score").inner_text().replace("\n", ""))
        shot(page, "3_summary")

        page.get_by_role("button", name="History").click()
        expect(page.get_by_text("Interview history")).to_be_visible()
        rows = page.locator("li").count()
        print("history rows:", rows)
        shot(page, "4_history")

        browser.close()
        if errors:
            raise SystemExit(f"page errors: {errors}")
        print("UI SMOKE TEST PASSED")


if __name__ == "__main__":
    main()
