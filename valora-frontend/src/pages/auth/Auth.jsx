import { useState } from "react";
import LoginForm from "../../components/auth/LoginForm";
import RegisterForm from "../../components/auth/RegisterForm";
import "../../styles/auth.css";
import bgVideo from "../../assets/valora-bg.mp4";

export default function Auth() {

  const [isLogin, setIsLogin] = useState(true);

  return (
    <div className="auth-container">

      <div className="auth-left">

  <div className="logo">
    Valora
  </div>

  {/* Illustration Area */}

  <div className="hero-image">

    <video
  className="hero-img"
  autoPlay
  loop
  muted
  playsInline
>
  <source src={bgVideo} type="video/mp4" />
</video>

  </div>

  {/* Text Section */}

  <div className="hero-text">

    {isLogin ? (
      <>
        <h2>Your AI-Powered Knowledge Base</h2>
        <p>
          Upload documents, chat with AI,
          and unlock insights from your data.
        </p>
      </>
    ) : (
      <>
        <h2>Start Your Journey to Smarter Knowledge</h2>
        <p>
          Join thousands of users leveraging AI
          to unlock insights.
        </p>
      </>
    )}

  </div>

</div>

      <div className="auth-right">

        <div className="form-container">

          <div className={`forms ${isLogin ? "show-login" : "show-register"}`}>

            <div className="form-panel">
              <LoginForm
                switchToRegister={() => setIsLogin(false)}
              />
            </div>

            <div className="form-panel">
              <RegisterForm
                switchToLogin={() => setIsLogin(true)}
              />
            </div>

          </div>

        </div>

      </div>

    </div>
  );
}