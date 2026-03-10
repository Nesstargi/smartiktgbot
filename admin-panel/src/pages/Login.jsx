import { useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../api/axios";
import { useAuth } from "../auth/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setSubmitting(true);

    try {
      const res = await api.post("/admin/auth/login", { email, password });
      login(res.data.access_token, res.data.user);
      navigate("/");
    } catch {
      setError("Неверный email или пароль");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="auth-wrap">
      <div className="auth-card">
        <h2>Вход в админку</h2>
        <form className="stack-form" onSubmit={handleSubmit}>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          {error && <p className="error-text">{error}</p>}

          <button type="submit" disabled={submitting}>
            {submitting ? "Входим..." : "Войти"}
          </button>
        </form>
      </div>
    </div>
  );
}
