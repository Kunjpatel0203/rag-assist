import { useState } from "react";
import { registerUser, resendVerification } from "../../services/authService";

export default function RegisterForm({ switchToLogin }) {

  const [form, setForm] = useState({
    fullName: "",
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
    company: "",
    role: ""
  });

  const [message, setMessage] = useState("");
  const [registeredEmail, setRegisteredEmail] = useState("");
  const [accepted, setAccepted] = useState(false);

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!accepted) {
      setMessage("Please accept the Terms of Service and Privacy Policy.");
      return;
    }

    try {

      await registerUser(form);

      setRegisteredEmail(form.email);

      setMessage(
        "Account created successfully. Please check your email to verify your account."
      );

    } catch (err) {

      if (err.response?.data?.message) {
        setMessage(err.response.data.message);
      } else {
        setMessage("Registration failed.");
      }

    }
  };

  const handleResend = async () => {

    if (!registeredEmail) {
      setMessage("Please register first to resend verification.");
      return;
    }

    try {

      const res = await resendVerification(registeredEmail);

      if (res.error) {
        setMessage(res.error);
      } else {
        setMessage("Verification email sent again.");
      }

    } catch {
      setMessage("Failed to resend email.");
    }

  };

  return (
    <form className="auth-form" onSubmit={handleSubmit}>

      <h2>Create an account</h2>
      <p>Start building your knowledge base</p>

      <input
        type="text"
        name="fullName"
        placeholder="Full Name"
        onChange={handleChange}
        required
      />

      <input
        type="text"
        name="username"
        placeholder="Username"
        onChange={handleChange}
      />

      <input
        type="email"
        name="email"
        placeholder="Email"
        onChange={handleChange}
        required
      />

      <div className="row">

        <input
          type="password"
          name="password"
          placeholder="Password"
          onChange={handleChange}
          required
        />

        <input
          type="password"
          name="confirmPassword"
          placeholder="Confirm"
          onChange={handleChange}
          required
        />

      </div>

      <div className="row">

        <input
          type="text"
          name="company"
          placeholder="Company (optional)"
          onChange={handleChange}
        />

        <input
          type="text"
          name="role"
          placeholder="Role (optional)"
          onChange={handleChange}
        />

      </div>

      {/* Terms Checkbox */}

      <label className="terms">

        <input
          type="checkbox"
          checked={accepted}
          onChange={(e) => setAccepted(e.target.checked)}
        />

        I agree to the Terms of Service and Privacy Policy

      </label>

      <button className="primary-btn">
        Create Account
      </button>

      {message && (
        <p className="message">{message}</p>
      )}

      {/* Resend Verification Link */}

      <div className="resend-box">

        <span>Didn't receive email?</span>

        <button
          type="button"
          onClick={handleResend}
          className="resend-btn"
        >
          Resend verification
        </button>

      </div>

      <p className="switch-text">

        Already have an account?

        <span onClick={switchToLogin}> Sign in</span>

      </p>

    </form>
  );
}