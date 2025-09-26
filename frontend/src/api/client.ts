// frontend/src/api/client.ts
const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

export async function apiFetch(path: string, opts: RequestInit = {}) {
  const token = localStorage.getItem("ff_token");
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((opts.headers as any) || {})
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(`${API_BASE}${path}`, { ...opts, headers });
  const text = await res.text();
  let json;
  try { json = text ? JSON.parse(text) : null } catch { json = text }
  if (!res.ok) throw new Error(json?.detail || res.statusText);
  return json;
}
