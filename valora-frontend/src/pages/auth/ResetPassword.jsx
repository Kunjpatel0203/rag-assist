import { useState } from "react";
import { resetPassword } from "../../services/authService";
import { useSearchParams, useNavigate } from "react-router-dom";

export default function ResetPassword() {

  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");

  const navigate = useNavigate();

  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {

    e.preventDefault();

    try {

      const res = await resetPassword({
        token: token,
        newPassword: password
      });

      if (res.error) {

        setMessage(res.error);

      } else {

        setMessage("Password reset successfully! Redirecting to login...");

        setTimeout(()=>{
          navigate("/auth");
        },2000);

      }

    } catch {

      setMessage("Reset failed.");

    }

  };

  return (

    <div className="auth-split">

      {/* LEFT SIDE */}

      <div className="auth-illustration">

        <div className="emoji">🔑</div>

        <h2>Reset Your Password</h2>

        <p>
          Choose a strong new password to secure
          your account.
        </p>

      </div>

      {/* RIGHT SIDE */}

      <div className="auth-form-side">

        <div className="auth-card">

          <h2>Reset Password</h2>

          <form onSubmit={handleSubmit}>

            <input
              type="password"
              placeholder="New Password"
              value={password}
              onChange={(e)=>setPassword(e.target.value)}
              required
            />

            <button className="primary-btn">
              Reset Password
            </button>

          </form>

          {message && (
            <p className="auth-message">{message}</p>
          )}

        </div>

      </div>

    </div>
  );
}