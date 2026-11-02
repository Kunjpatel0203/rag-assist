import "../styles/landing.css";
import { useNavigate } from "react-router-dom";

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div className="landing-container">

      {/* NAVBAR */}
    {/* NAVBAR */}
<nav className="navbar">

  {/* LOGO */}
  <div className="nav-logo">
    <div className="logo-icon">V</div>
    <span>Valora</span>
  </div>

  {/* MENU */}
  <div className="nav-menu">
    <span className="nav-item active">Features</span>
    <span className="nav-item">How it works</span>
    <span className="nav-item">Pricing</span>
    <span className="nav-item">Docs</span>
  </div>

  {/* SIGN IN */}
  <button
    className="nav-btn"
    onClick={() => navigate("/login")}
  >
    Sign In
  </button>

</nav>
      {/* HERO */}
      {/* HERO */}
<section className="hero-section">

  <div className="hero-glow"></div>

  <div className="hero-content">

    

    <h1 className="hero-title">
      Your documents,
      <br />
      <span>unlocked by AI</span>
    </h1>

    <p className="hero-subtitle">
      Upload files, build knowledge workspaces, and chat with your data.
      Get instant answers, summaries, and insights — all in one place.
    </p>

    <button
      className="hero-btn"
      onClick={() => navigate("/login")}
    >
      Get Started
    </button>

  </div>

</section>

      {/* TRUSTED */}
      <section className="trusted">
        <p>TRUSTED BY TEAMS AT</p>
        <div className="brands">
          <span>Notion</span>
          <span>Linear</span>
          <span>Vercel</span>
          <span>Stripe</span>
          <span>Figma</span>
        </div>
      </section>

      {/* FEATURES */}
      {/* FEATURES */}
<section className="features-section">
  <div className="features-container">

    <p className="features-label">FEATURES</p>

    <h2 className="features-title">
      Everything you need to work smarter with docs
    </h2>

    <p className="features-subtitle">
      From upload to insight in seconds. Knowledge Vault handles the heavy
      lifting so your team can focus on what matters.
    </p>

    <div className="features-grid">

      {[
        {
          title: "AI-Powered Chat",
          desc: "Ask questions, get summaries, and extract insights from your documents using natural language — no queries needed."
        },
        {
          title: "Multi-format Support",
          desc: "Upload PDFs, DOCX, XLSX, TXT, Markdown, and more. All documents are indexed automatically on upload."
        },
        {
          title: "Smart Workspaces",
          desc: "Organize documents into workspaces by project or team. Share with colleagues and collaborate in real time."
        },
        {
          title: "Instant Indexing",
          desc: "Documents are chunked and indexed in seconds. Ask questions immediately after upload — no waiting."
        },
        {
          title: "Private & Secure",
          desc: "Your data never trains AI models. All files are encrypted at rest and in transit with enterprise-grade security."
        },
        {
          title: "Source Citations",
          desc: "Every AI answer links back to the exact document and page it came from — full transparency, zero hallucinations."
        }
      ].map((f, i) => (
        <div key={i} className="feature-card">
          <div className="feature-icon"></div>
          <h3>{f.title}</h3>
          <p>{f.desc}</p>
        </div>
      ))}

    </div>
  </div>
</section>

      {/* HOW IT WORKS */}
<section className="how-section">

  <p className="how-label">HOW IT WORKS</p>

  <h2 className="how-title">Up and running in 3 steps</h2>

  <p className="how-subtitle">
    No setup, no training required. Just upload and start asking.
  </p>

  <div className="steps-wrapper">

    <div className="step-block">
      <div className="step-circle">1</div>
      <h3>Create a workspace</h3>
      <p>
        Name your workspace and invite teammates. Group documents by project,
        client, or topic.
      </p>
    </div>

    <div className="step-block">
      <div className="step-circle">2</div>
      <h3>Upload your documents</h3>
      <p>
        Drag and drop files or connect cloud sources. AI indexes everything instantly.
      </p>
    </div>

    <div className="step-block">
      <div className="step-circle">3</div>
      <h3>Chat and get answers</h3>
      <p>
        Ask anything in plain language. Get cited, accurate answers from your own data.
      </p>
    </div>

    {/* dotted line */}
    <div className="steps-line"></div>

  </div>

</section>


{/* CTA */}
<section className="cta-section">
  <div className="cta-box">

    <h2>Ready to unlock your knowledge?</h2>

    <p>
      Join thousands of teams already using Knowledge Vault to work smarter.
    </p>

    <button
      className="hero-btn"
      onClick={() => navigate("/login")}
    >
      Get Started
    </button>

  </div>
</section>

      {/* FOOTER */}
      <footer className="footer">
        © 2026 Knowledge Vault · Privacy · Terms · Contact
      </footer>
    </div>
  );
}