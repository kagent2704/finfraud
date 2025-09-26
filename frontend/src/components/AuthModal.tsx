import React, { useState } from "react";
import { useAuth } from "../context/AuthContext";

export default function AuthModal({ open, onClose }: { open: boolean; onClose: () => void; }) {
  const [tab, setTab] = useState<"signin"|"signup">("signin");
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState<string|null>(null);
  const auth = useAuth();

  if (!open) return null;

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    try {
      setErr(null);
      if (tab === "signin") {
        await auth.login(email, password);
      } else {
        await auth.signup(name, email, password);
      }
      onClose();
    } catch (err: any) {
      setErr(err.message || String(err));
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white/6 backdrop-blur-md rounded-2xl p-6 w-full max-w-md text-white">
        <div className="flex justify-between mb-4">
          <button onClick={() => setTab("signin")} className={`px-3 py-1 ${tab==="signin" ? "underline" : "text-gray-300"}`}>Sign In</button>
          <button onClick={() => setTab("signup")} className={`px-3 py-1 ${tab==="signup" ? "underline" : "text-gray-300"}`}>Sign Up</button>
        </div>

        <form onSubmit={submit} className="space-y-3">
          {tab === "signup" && (
            <input value={name} onChange={e=>setName(e.target.value)} placeholder="Full name" className="w-full px-3 py-2 rounded-lg bg-white/10" />
          )}
          <input value={email} onChange={e=>setEmail(e.target.value)} placeholder="Email" className="w-full px-3 py-2 rounded-lg bg-white/10" />
          <input value={password} onChange={e=>setPassword(e.target.value)} placeholder="Password" type="password" className="w-full px-3 py-2 rounded-lg bg-white/10" />
          {err && <div className="text-red-400">{err}</div>}
          <button className="w-full bg-indigo-600 py-2 rounded-lg">{tab === "signin" ? "Sign In" : "Create account"}</button>
        </form>

        <button onClick={onClose} className="mt-3 w-full text-sm text-gray-300">Cancel</button>
      </div>
    </div>
  );
}
