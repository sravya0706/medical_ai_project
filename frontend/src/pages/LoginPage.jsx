import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { extractErrorMessage } from "../services/api";
import "./AuthLayout.css";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      navigate("/chat");
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="card auth-card">
        <div className="auth-card__brand">
          <span className="auth-card__brand-mark">M</span>
          <span className="auth-card__brand-name">MediAssist</span>
        </div>

        <div>
          <h1>Welcome back</h1>
          <p className="auth-card__subtitle">Sign in to continue your consultation.</p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
            />
          </div>
          <div className="field">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
            />
          </div>

          {error && <p className="error-text">{error}</p>}

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? "Signing in…" : "Sign in"}
          </button>
        </form>

        <p className="auth-card__footer">
          Don't have an account? <Link to="/register">Create one</Link>
        </p>

        <p className="auth-card__disclaimer">
          MediAssist provides general information only and does not replace
          professional medical advice.
        </p>
      </div>
    </div>
  );
}
