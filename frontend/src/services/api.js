import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: BASE_URL,
});

// Automatically attach the JWT to every outgoing request — components and
// other services never have to know about auth headers directly.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("mediassist_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// A 401 from the backend means the token is invalid/expired — clear it and
// let the app redirect to login rather than showing a confusing error.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("mediassist_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export function extractErrorMessage(error) {
  return (
    error?.response?.data?.detail ||
    error?.response?.data?.error ||
    error?.message ||
    "Something went wrong. Please try again."
  );
}
