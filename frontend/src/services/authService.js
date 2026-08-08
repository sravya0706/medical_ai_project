import { api } from "./api";

export async function register(email, password) {
  const { data } = await api.post("/api/v1/auth/register", { email, password });
  return data;
}

export async function login(email, password) {
  const { data } = await api.post("/api/v1/auth/login", { email, password });
  return data;
}
