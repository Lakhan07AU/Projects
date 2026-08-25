"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api, clearTokens, getAccessToken, setTokens } from "./api";

export interface AuthUser {
  id: number;
  email: string;
  full_name: string;
  role: string;
}

interface AuthState {
  user: AuthUser | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthState>({
  user: null,
  loading: true,
  login: async () => {},
  register: async () => {},
  logout: async () => {},
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  const loadMe = useCallback(async () => {
    if (!getAccessToken()) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const me = await api<AuthUser>("/auth/me");
      setUser(me);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadMe();
  }, [loadMe]);

  const login = useCallback(async (email: string, password: string) => {
    const tokens = await api<{ access_token: string; refresh_token: string }>("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    setTokens(tokens.access_token, tokens.refresh_token);
    await loadMe();
  }, [loadMe]);

  const register = useCallback(
    async (email: string, password: string, fullName: string) => {
      const tokens = await api<{ access_token: string; refresh_token: string }>("/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, full_name: fullName }),
      });
      setTokens(tokens.access_token, tokens.refresh_token);
      await loadMe();
    },
    [loadMe],
  );

  const logout = useCallback(async () => {
    try {
      const refresh =
        typeof window !== "undefined" ? localStorage.getItem("cg_refresh") : null;
      if (refresh) {
        await api("/auth/logout", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ refresh_token: refresh }),
        }).catch(() => undefined);
      }
    } finally {
      clearTokens();
      setUser(null);
    }
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
