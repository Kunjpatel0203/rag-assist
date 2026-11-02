import { useState } from "react";
import { loginUser } from "../../services/authService";
import { useNavigate } from "react-router-dom";

export default function LoginForm({ switchToRegister }) {

  const navigate = useNavigate();

  const [form, setForm] = useState({
    email: "",
    password: ""
  });

  const [error, setError] = useState("");

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const res = await loginUser(form);

      if (res.error) {
        setError(res.error);
        return;
      }

      localStorage.setItem("token", res.token);

      navigate("/dashboard");

    } catch (err) {
      setError("Login failed");
    }
  };

  return (
    <form className="auth-form" onSubmit={handleSubmit}>

      <h2>Welcome back</h2>
      <p>Sign in to your account to continue</p>

      <input
        type="email"
        name="email"
        placeholder="you@example.com"
        value={form.email}
        onChange={handleChange}
        required
      />

      <input
        type="password"
        name="password"
        placeholder="Password"
        value={form.password}
        onChange={handleChange}
        required
      />

      <a href="/forgot-password" className="forgot-link">
        Forgot password?
      </a>

      {error && <p className="error">{error}</p>}

      <button type="submit" className="primary-btn">
        Sign In
      </button>

      <p className="switch-text">
        New to Knowledge Vault?
        <span onClick={switchToRegister}> Create an account</span>
      </p>

    </form>
  );
}