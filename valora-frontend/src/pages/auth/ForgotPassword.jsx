import { useState } from "react";
import { forgotPassword } from "../../services/authService";
import { Link } from "react-router-dom";

export default function ForgotPassword() {

  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {

    e.preventDefault();

    try {

      const res = await forgotPassword(email);

      if (res.error) {
        setMessage(res.error);
      } else {
        setMessage("Reset link sent! Please check your email.");
      }

    } catch {
      setMessage("Something went wrong.");
    }

  };

  return (

    <div className="auth-split">

      {/* LEFT SIDE */}

      <div className="auth-illustration">

        <div className="emoji">🔐</div>

        <h2>Forgot Your Password?</h2>

        <p>
          No worries. Enter your email and we'll send
          you a secure reset link.
        </p>

      </div>

      {/* RIGHT SIDE */}

      <div className="auth-form-side">

        <div className="auth-card">

          <h2>Forgot Password</h2>

          <form onSubmit={handleSubmit}>

            <input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e)=>setEmail(e.target.value)}
              required
            />

            <button className="primary-btn">
              Send Reset Link
            </button>

          </form>

          {message && (
            <p className="auth-message">{message}</p>
          )}

          <div className="auth-footer">
            <Link to="/auth">Back to Login</Link>
          </div>

        </div>

      </div>

    </div>
  );
}