import React, { createContext, useContext, useEffect, useState } from "react";
import { apiFetch } from "../api/client";

type User = { user_id: number; email?: string };

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<any>;
  signup: (name: string, email: string, password: string) => Promise<any>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);

  // ✅ Restore session on page load
  useEffect(() => {
    const token = localStorage.getItem("ff_token");
    if (token) {
      refreshUser();
    }
  }, []);

  async function login(email: string, password: string) {
    const res = await apiFetch("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });

    localStorage.setItem("ff_token", res.access_token);
    setUser({ user_id: res.user_id, email });
    return res;
  }

  async function signup(name: string, email: string, password: string) {
    const res = await apiFetch("/auth/signup", {
      method: "POST",
      body: JSON.stringify({ name, email, password }),
    });

    // ✅ if your backend returns a token after signup
    if (res.access_token) {
      localStorage.setItem("ff_token", res.access_token);
      setUser({ user_id: res.user_id, email });
    }
    return res;
  }

  async function refreshUser() {
    try {
      const res = await apiFetch("/auth/me", { method: "GET" });
      setUser({ user_id: res.id, email: res.email });
    } catch (err) {
      console.warn("⚠️ Failed to refresh user:", err);
      logout();
    }
  }

  function logout() {
    localStorage.removeItem("ff_token");
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, login, signup, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
};
