"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
} from "react";
import useSWR from "swr";
import {
  api,
  clearToken,
  getToken,
  setToken,
  type User,
} from "@/lib/api";

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: unknown;
  login: (email: string, password: string) => Promise<User>;
  logout: () => void;
  refresh: () => Promise<User | undefined>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const hasToken = typeof window !== "undefined" && !!getToken();

  const {
    data: user,
    error,
    isLoading,
    mutate,
  } = useSWR<User>(hasToken ? "auth/me" : null, () => api.me(), {
    revalidateOnFocus: false,
    shouldRetryOnError: false,
  });

  const login = useCallback(
    async (email: string, password: string): Promise<User> => {
      const { access_token } = await api.login({ email, password });
      setToken(access_token);
      const me = await api.me();
      await mutate(me, { revalidate: false });
      return me;
    },
    [mutate]
  );

  const logout = useCallback(() => {
    clearToken();
    void mutate(undefined, { revalidate: false });
    if (typeof window !== "undefined") {
      window.location.href = "/login";
    }
  }, [mutate]);

  const refresh = useCallback(() => mutate(), [mutate]);

  const value = useMemo<AuthContextValue>(
    () => ({
      user: user ?? null,
      isLoading: hasToken ? isLoading : false,
      isAuthenticated: !!user,
      error,
      login,
      logout,
      refresh,
    }),
    [user, hasToken, isLoading, error, login, logout, refresh]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an <AuthProvider>");
  }
  return ctx;
}
