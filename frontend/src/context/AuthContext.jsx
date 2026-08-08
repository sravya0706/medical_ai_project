import { createContext, useContext, useState, useCallback } from "react";
import * as authService from "../services/authService";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("mediassist_token"));

  const login = useCallback(async (email, password) => {
    const data = await authService.login(email, password);
    localStorage.setItem("mediassist_token", data.access_token);
    setToken(data.access_token);
  }, []);

  const register = useCallback(async (email, password) => {
    const data = await authService.register(email, password);
    localStorage.setItem("mediassist_token", data.access_token);
    setToken(data.access_token);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("mediassist_token");
    setToken(null);
  }, []);

  const value = {
    token,
    isAuthenticated: !!token,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
