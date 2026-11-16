import { useEffect, useState } from "react";
import { api } from "./api.js";
import { Button, Card, CRITERIA, ErrorBox, EvaluationCard, MockBadge, ROLES } from "./components.jsx";

// Views: setup -> interview -> summary; history is reachable from the header.
export default function App() {
  const [view, setView] = useState("setup");
  const [session, setSession] = useState(null);
  const [health, setHealth] = useState(null);

  useEffect(() => {
    api.health().then(setHealth).catch(() => setHealth({ status: "down" }));
  }, []);

  const openSession = async (id) => {
    const s = await api.getSession(id);
    setSession(s);
    setView(s.status === "finished" ? "summary" : "interview");
  };

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <header className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <button onClick={() => setView("setup")} className="text-left">
          <h1 className="text-2xl font-bold">AI Interview Coach</h1>
          <p className="text-sm text-slate-500">Practice interviews · STAR-based AI feedback</p>
        </button>
        <div className="flex items-center gap-3">
          <BackendStatus health={health} />
          <Button variant="secondary" onClick={() => setView("history")}>History</Button>
        </div>
      </header>

      {view === "setup" && <Setup onStarted={(s) => { setSession(s); setView("interview"); }} />}
      {view === "interview" && session && (
        <Interview key={session.id} session={session} setSession={setSession} onFinished={(s) => { setSession(s); setView("summary"); }} />
      )}
      {view === "summary" && session && <Summary session={session} onRestart={() => setView("setup")} />}
      {view === "history" && <History onOpen={openSession} />}
    </div>
  );
}

function BackendStatus({ health }) {
  if (!health) return <span className="text-xs text-slate-400">checking backend…</span>;
  if (health.status !== "ok") return <span className="text-xs text-red-600">backend offline</span>;
  if (!health.llm_ready) return <span className="text-xs text-red-600" title={health.detail}>LLM not configured</span>;
  return health.is_mock ? <MockBadge isMock /> : <span className="text-xs text-emerald-700">AI: {health.llm_provider}</span>;
}

function Setup({ onStarted }) {
  const [role, setRole] = useState("data_analyst");
  const [language, setLanguage] = useState("en");
  const [level, setLevel] = useState("intern");
  const [numQuestions, setNumQuestions] = useState(7);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const start = async () => {
    setLoading(true);
    setError(null);
    try {
      onStarted(await api.createSession({ role, language, level, num_questions: numQuestions }));
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const Choice = ({ value, current, set, children }) => (
    <button
      onClick={() => set(value)}
      className={`rounded-lg border px-3 py-2 text-sm ${current === value ? "border-indigo-600 bg-indigo-50 font-semibold text-indigo-700" : "border-slate-300 bg-white"}`}
    >
      {children}
    </button>
  );

  return (
    <Card className="space-y-5">
      <h2 className="text-lg font-semibold">Set up your interview</h2>
      <div>
        <div className="mb-2 text-sm font-medium">Job role</div>
        <div className="flex flex-wrap gap-2">
          {ROLES.map((r) => <Choice key={r.id} value={r.id} current={role} set={setRole}>{r.label}</Choice>)}
        </div>
      </div>
      <div className="grid gap-5 sm:grid-cols-3">
        <div>
          <div className="mb-2 text-sm font-medium">Language</div>
          <div className="flex gap-2">
            <Choice value="en" current={language} set={setLanguage}>English</Choice>
            <Choice value="ru" current={language} set={setLanguage}>Русский</Choice>
          </div>
        </div>
        <div>
          <div className="mb-2 text-sm font-medium">Experience level</div>
          <div className="flex gap-2">
            <Choice value="intern" current={level} set={setLevel}>Intern</Choice>
            <Choice value="junior" current={level} set={setLevel}>Junior</Choice>
          </div>
        </div>
        <div>
          <label className="mb-2 block text-sm font-medium" htmlFor="numq">Questions</label>
          <select id="numq" value={numQuestions} onChange={(e) => setNumQuestions(Number(e.target.value))} className="rounded-lg border border-slate-300 px-3 py-2 text-sm">
            {[6, 7, 8].map((n) => <option key={n} value={n}>{n}</option>)}
          </select>
        </div>
      </div>
      <ErrorBox error={error} />
      <Button onClick={start} disabled={loading}>{loading ? "Generating questions…" : "Start interview"}</Button>
    </Card>
  );
}

function Interview({ session, setSession, onFinished }) {
  const firstOpen = session.questions.findIndex((q) => !q.answer);
  const [idx, setIdx] = useState(firstOpen === -1 ? 0 : firstOpen);
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  const q = session.questions[idx];
  const answeredCount = session.questions.filter((x) => x.answer).length;

  const submit = async () => {
    setBusy(true);
    setError(null);
    try {
      const ans = await api.submitAnswer(q.id, draft);
      setSession({ ...session, questions: session.questions.map((x) => (x.id === q.id ? { ...x, answer: ans } : x)) });
      setDraft("");
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  const finish = async () => {
    setBusy(true);
    setError(null);
    try {
      onFinished(await api.finish(session.id));
    } catch (e) {
      setError(e.message);
      setBusy(false);
    }
  };

  const go = (i) => { setIdx(i); setDraft(""); setError(null); };

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2 text-sm text-slate-600">
        <span>{session.role_label} · {session.level} · {session.language.toUpperCase()}</span>
        <span>{answeredCount}/{session.questions.length} answered</span>
      </div>
      <div className="flex flex-wrap gap-1">
        {session.questions.map((x, i) => (
          <button key={x.id} onClick={() => go(i)} aria-label={`Question ${i + 1}`}
            className={`h-8 w-8 rounded text-sm ${i === idx ? "bg-indigo-600 text-white" : x.answer ? "bg-emerald-100 text-emerald-800" : "bg-slate-200"}`}>
            {i + 1}
          </button>
        ))}
      </div>

      <Card className="space-y-3">
        <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">
          Question {idx + 1} of {session.questions.length} · {q.category}
        </div>
        <p className="text-lg" data-testid="question-text">{q.text}</p>
        <textarea
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          rows={6}
          maxLength={5000}
          placeholder={q.answer ? "Write a new attempt to replace your previous answer…" : "Type your answer. Tip: Situation → Task → Action → Result."}
          className="w-full rounded-lg border border-slate-300 p-3 text-sm focus:border-indigo-500 focus:outline-none"
        />
        <ErrorBox error={error} />
        <div className="flex flex-wrap gap-2">
          <Button onClick={submit} disabled={busy || !draft.trim()}>{busy ? "Evaluating…" : q.answer ? "Re-submit answer" : "Submit answer"}</Button>
          {idx < session.questions.length - 1 && <Button variant="secondary" onClick={() => go(idx + 1)}>Next question →</Button>}
          <Button variant="secondary" onClick={finish} disabled={busy || answeredCount === 0} className="ml-auto">Finish interview</Button>
        </div>
      </Card>

      {q.answer && (
        <>
          <Card className="text-sm"><span className="font-semibold">Your answer: </span>{q.answer.text}</Card>
          <EvaluationCard evaluation={q.answer.evaluation} />
        </>
      )}
    </div>
  );
}

function Summary({ session, onRestart }) {
  const s = session.summary;
  const label = (k) => CRITERIA.find((c) => c.key === k)?.label ?? k;
  return (
    <div className="space-y-4">
      <Card className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Interview summary</h2>
          <MockBadge isMock={session.is_mock} />
        </div>
        <p className="text-sm text-slate-600">{session.role_label} · {session.level} · answered {s.answered} of {s.total_questions}</p>
        <div className="text-4xl font-bold" data-testid="overall-score">{s.overall}<span className="text-lg text-slate-400">/5</span></div>
        <div className="grid gap-3 sm:grid-cols-3">
          {CRITERIA.map((c) => (
            <div key={c.key} className="rounded-lg bg-slate-50 p-3">
              <div className="text-xs text-slate-500">{c.label}</div>
              <div className="text-xl font-semibold">{s.averages[c.key]}</div>
            </div>
          ))}
        </div>
        <p className="text-sm">Strongest: <b>{label(s.strongest_criterion)}</b> · Needs work: <b>{label(s.weakest_criterion)}</b></p>
        <div>
          <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">Priority fixes</div>
          <ol className="mt-1 list-decimal pl-5 text-sm">{s.priority_fixes.map((f, i) => <li key={i}>{f}</li>)}</ol>
        </div>
        <Button onClick={onRestart}>Start a new interview</Button>
      </Card>
      {session.questions.filter((q) => q.answer).map((q) => (
        <details key={q.id} className="rounded-xl border border-slate-200 bg-white p-4">
          <summary className="cursor-pointer text-sm font-medium">Q{q.position}. {q.text} — {q.answer.evaluation.average}/5</summary>
          <p className="mt-3 text-sm"><b>Your answer:</b> {q.answer.text}</p>
          <div className="mt-3"><EvaluationCard evaluation={q.answer.evaluation} /></div>
        </details>
      ))}
    </div>
  );
}

function History({ onOpen }) {
  const [items, setItems] = useState(null);
  const [error, setError] = useState(null);
  useEffect(() => { api.listSessions().then(setItems).catch((e) => setError(e.message)); }, []);
  return (
    <Card className="space-y-3">
      <h2 className="text-lg font-semibold">Interview history</h2>
      <ErrorBox error={error} />
      {items?.length === 0 && <p className="text-sm text-slate-500">No interviews yet.</p>}
      <ul className="divide-y divide-slate-100">
        {items?.map((it) => (
          <li key={it.id} className="flex items-center justify-between py-2 text-sm">
            <span>
              #{it.id} · {it.role_label} · {it.level} · {it.language.toUpperCase()} · {new Date(it.created_at).toLocaleString()}
              {it.provider === "mock" && <span className="ml-2 text-xs text-amber-700">(mock)</span>}
            </span>
            <span className="flex items-center gap-3">
              <span className={it.status === "finished" ? "font-semibold" : "text-slate-500"}>
                {it.status === "finished" ? `${it.overall}/5` : `${it.answered}/${it.total_questions} in progress`}
              </span>
              <Button variant="secondary" onClick={() => onOpen(it.id)}>Open</Button>
            </span>
          </li>
        ))}
      </ul>
    </Card>
  );
}
