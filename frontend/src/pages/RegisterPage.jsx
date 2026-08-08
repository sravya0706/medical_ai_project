import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { extractErrorMessage } from "../services/api";
import "./AuthLayout.css";

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }

    setLoading(true);
    try {
      await register(email, password);
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
          <h1>Create your account</h1>
          <p className="auth-card__subtitle">Start a private, secure conversation.</p>
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
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="new-password"
            />
          </div>

          {error && <p className="error-text">{error}</p>}

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? "Creating account…" : "Create account"}
          </button>
        </form>

        <p className="auth-card__footer">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>

        <p className="auth-card__disclaimer">
          MediAssist provides general information only and does not replace
          professional medical advice.
        </p>
      </div>
    </div>
  );
}
