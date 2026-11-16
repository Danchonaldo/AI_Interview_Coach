import { useState } from "react";

export const ROLES = [
  { id: "data_analyst", label: "Data Analyst" },
  { id: "marketing_intern", label: "Marketing Intern" },
  { id: "python_developer", label: "Python Developer" },
];
export const CRITERIA = [
  { key: "relevance", label: "Relevance" },
  { key: "structure", label: "Structure (STAR)" },
  { key: "specificity", label: "Specificity" },
];

export function Card({ children, className = "" }) {
  return <div className={`rounded-xl border border-slate-200 bg-white p-5 shadow-sm ${className}`}>{children}</div>;
}

export function Button({ children, variant = "primary", className = "", ...props }) {
  const styles = {
    primary: "bg-indigo-600 text-white hover:bg-indigo-700 disabled:bg-indigo-300",
    secondary: "bg-white text-slate-700 border border-slate-300 hover:bg-slate-50 disabled:text-slate-400",
  };
  return (
    <button className={`rounded-lg px-4 py-2 text-sm font-medium transition ${styles[variant]} ${className}`} {...props}>
      {children}
    </button>
  );
}

export function ErrorBox({ error }) {
  if (!error) return null;
  return <div role="alert" className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>;
}

export function MockBadge({ isMock }) {
  if (!isMock) return null;
  return (
    <span className="rounded bg-amber-100 px-2 py-0.5 text-xs font-semibold text-amber-800" title="LLM_PROVIDER=mock: heuristic output, not real AI">
      MOCK MODE — not real AI
    </span>
  );
}

function ScoreBar({ label, value }) {
  const color = value >= 4 ? "bg-emerald-500" : value >= 3 ? "bg-amber-400" : "bg-red-400";
  return (
    <div>
      <div className="flex justify-between text-sm">
        <span>{label}</span>
        <span className="font-semibold" data-testid={`score-${label}`}>{value}/5</span>
      </div>
      <div className="mt-1 h-2 rounded bg-slate-100">
        <div className={`h-2 rounded ${color}`} style={{ width: `${(value / 5) * 100}%` }} />
      </div>
    </div>
  );
}

export function EvaluationCard({ evaluation }) {
  const [showImproved, setShowImproved] = useState(true);
  return (
    <Card className="space-y-4 border-indigo-200" >
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Evaluation · average {evaluation.average}/5</h3>
        <MockBadge isMock={evaluation.is_mock} />
      </div>
      <div className="grid gap-3 sm:grid-cols-3">
        {CRITERIA.map((c) => <ScoreBar key={c.key} label={c.label} value={evaluation[c.key]} />)}
      </div>
      <div className="rounded-lg bg-indigo-50 p-3">
        <div className="text-xs font-semibold uppercase tracking-wide text-indigo-700">Most important fix</div>
        <p className="mt-1 text-sm">{evaluation.top_fix}</p>
      </div>
      <div>
        <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">Feedback</div>
        <p className="mt-1 whitespace-pre-line text-sm">{evaluation.feedback}</p>
      </div>
      <div>
        <button className="text-xs font-semibold uppercase tracking-wide text-slate-500 hover:text-slate-800" onClick={() => setShowImproved((v) => !v)}>
          Improved answer {showImproved ? "▲" : "▼"}
        </button>
        {showImproved && <p className="mt-1 whitespace-pre-line rounded-lg bg-slate-50 p-3 text-sm">{evaluation.improved_answer}</p>}
      </div>
    </Card>
  );
}
