// Thin client for the FastAPI backend (proxied at /api by Vite). No secrets here.
const BASE = import.meta.env.VITE_API_BASE || "/api";

async function request(path, options = {}) {
  const res = await fetch(BASE + path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    const detail = data?.detail;
    const msg = Array.isArray(detail)
      ? detail.map((d) => d.msg).join("; ")
      : detail || `Request failed (${res.status})`;
    throw new Error(msg);
  }
  return data;
}

export const api = {
  health: () => request("/health"),
  createSession: (body) => request("/sessions", { method: "POST", body: JSON.stringify(body) }),
  getSession: (id) => request(`/sessions/${id}`),
  listSessions: () => request("/sessions"),
  submitAnswer: (questionId, text) =>
    request(`/questions/${questionId}/answers`, { method: "POST", body: JSON.stringify({ text }) }),
  finish: (id) => request(`/sessions/${id}/finish`, { method: "POST" }),
};
