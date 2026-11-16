from fastapi.testclient import TestClient

from app.llm import Evaluation, LLMError, MockProvider, QuestionSet
from app.main import create_app

GOOD_ANSWER = (
    "In my internship last year the situation was that weekly reports took two days. "
    "My task was to automate them. I used Python and pandas, I wrote a script and I built "
    "a dashboard in Power BI. As a result report time was reduced by 80% and I learned SQL."
)


def start(client, **kw):
    body = {"role": "data_analyst", "language": "en", "level": "intern", **kw}
    r = client.post("/sessions", json=body)
    assert r.status_code == 201, r.text
    return r.json()


def test_health_reports_mock(client):
    r = client.get("/health").json()
    assert r["llm_provider"] == "mock" and r["is_mock"] is True and r["llm_ready"] is True


def test_full_flow(client):
    s = start(client, num_questions=7)
    assert s["status"] == "in_progress" and s["is_mock"] is True
    assert len(s["questions"]) == 7
    assert [q["position"] for q in s["questions"]] == list(range(1, 8))

    q1, q2 = s["questions"][0], s["questions"][1]
    r = client.post(f"/questions/{q1['id']}/answers", json={"text": GOOD_ANSWER})
    assert r.status_code == 201, r.text
    ev = r.json()["evaluation"]
    for k in ("relevance", "structure", "specificity"):
        assert 1 <= ev[k] <= 5
    assert ev["feedback"] and ev["improved_answer"] and ev["top_fix"]

    weak = client.post(f"/questions/{q2['id']}/answers", json={"text": "I like data."}).json()["evaluation"]
    assert weak["average"] < ev["average"], "mock grader should rank a vague answer lower"

    got = client.get(f"/sessions/{s['id']}").json()
    assert got["questions"][0]["answer"]["text"] == GOOD_ANSWER

    fin = client.post(f"/sessions/{s['id']}/finish")
    assert fin.status_code == 200, fin.text
    summary = fin.json()["summary"]
    assert fin.json()["status"] == "finished"
    assert summary["answered"] == 2 and summary["total_questions"] == 7
    assert 1 <= summary["overall"] <= 5
    assert summary["weakest_question_id"] == q2["id"]
    assert summary["priority_fixes"]

    # finished sessions are read-only, finish is idempotent
    assert client.post(f"/questions/{q1['id']}/answers", json={"text": "x"}).status_code == 409
    assert client.post(f"/sessions/{s['id']}/finish").json()["summary"] == summary

    hist = client.get("/sessions").json()
    assert hist[0]["id"] == s["id"] and hist[0]["overall"] == summary["overall"]


def test_russian_and_junior(client):
    s = start(client, role="python_developer", language="ru", level="junior", num_questions=6)
    assert len(s["questions"]) == 6
    assert any("а" <= ch <= "я" for ch in s["questions"][0]["text"].lower())
    r = client.post(f"/questions/{s['questions'][0]['id']}/answers", json={"text": "Я написал бота на Python."})
    assert "MOCK" in r.json()["evaluation"]["feedback"]


def test_reanswer_replaces(client):
    s = start(client)
    qid = s["questions"][0]["id"]
    client.post(f"/questions/{qid}/answers", json={"text": "first"})
    client.post(f"/questions/{qid}/answers", json={"text": GOOD_ANSWER})
    got = client.get(f"/sessions/{s['id']}").json()
    assert got["questions"][0]["answer"]["text"] == GOOD_ANSWER


def test_validation_and_errors(client):
    assert client.post("/sessions", json={"role": "astronaut"}).status_code == 422
    assert client.post("/sessions", json={"role": "data_analyst", "num_questions": 9}).status_code == 422
    assert client.post("/sessions", json={"role": "data_analyst", "language": "de"}).status_code == 422
    assert client.get("/sessions/999").status_code == 404
    assert client.post("/questions/999/answers", json={"text": "hi"}).status_code == 404
    s = start(client)
    qid = s["questions"][0]["id"]
    assert client.post(f"/questions/{qid}/answers", json={"text": "   "}).status_code == 422
    assert client.post(f"/questions/{qid}/answers", json={"text": "x" * 5001}).status_code == 422
    assert client.post(f"/sessions/{s['id']}/finish").status_code == 400  # nothing answered


def test_persistence_across_restart(db_url):
    app1 = create_app(database_url=db_url, provider_factory=MockProvider)
    with TestClient(app1) as c:
        s = start(c)
        c.post(f"/questions/{s['questions'][0]['id']}/answers", json={"text": GOOD_ANSWER})
        c.post(f"/sessions/{s['id']}/finish")
    app2 = create_app(database_url=db_url, provider_factory=MockProvider)  # "restart"
    with TestClient(app2) as c:
        got = c.get(f"/sessions/{s['id']}").json()
        assert got["status"] == "finished" and got["summary"]["answered"] == 1


class _BrokenProvider:
    name, is_mock = "broken", False

    def generate_questions(self, *a) -> QuestionSet:
        raise LLMError("boom")

    def evaluate_answer(self, *a) -> Evaluation:
        raise LLMError("boom")


def test_llm_failure_returns_502_and_saves_nothing(db_url):
    app = create_app(database_url=db_url, provider_factory=_BrokenProvider)
    with TestClient(app) as c:
        assert c.post("/sessions", json={"role": "data_analyst"}).status_code == 502
        assert c.get("/sessions").json() == []
