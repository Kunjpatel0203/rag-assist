import "../../styles/login.css";
import { useState } from "react";


export default function Login() {

  const [mode,setMode] = useState("login")

  const [name,setName] = useState("")
  const [email,setEmail] = useState("")
  const [password,setPassword] = useState("")
  const [confirmPassword,setConfirmPassword] = useState("")

  const handleLogin = async (e) => {
    e.preventDefault()

    const response = await fetch("http://localhost:8080/auth/login",{
      method:"POST",
      headers:{ "Content-Type":"application/json" },
      body:JSON.stringify({email,password})
    })

    const data = await response.json()

    if(response.ok && data.token){
      localStorage.setItem("token",data.token)
      window.location.href="/dashboard"
    }else{
      alert(data.error || "Login failed")
    }
  }

  const handleRegister = async (e) => {
    e.preventDefault()

    if(password!==confirmPassword){
      alert("Passwords do not match")
      return
    }

    const response = await fetch("http://localhost:8080/auth/register",{
      method:"POST",
      headers:{ "Content-Type":"application/json" },
      body:JSON.stringify({
        name,
        email,
        password
      })
    })

    const data = await response.json()

    if(response.ok){
      alert("Account created. Please login.")
      setMode("login")
    }else{
      alert(data.error || "Registration failed")
    }
  }

  return (

    <div className="auth-page">

      {/* LEFT PANEL */}

      <div className="auth-left">
  <img src="/valora-bg.png" className="auth-bg-img" />

  <div className="bg-overlay"></div>

  <div className="auth-content">
    <h1>Valora</h1>
    <p>Hybrid RAG Intelligence Platform</p>

    <h2>Your AI-Powered Knowledge Base</h2>
    <p>Upload documents, chat with AI, and unlock insights.</p>
  </div>
</div>


      {/* RIGHT PANEL */}

      <div className="auth-right">

        <div className={`form-wrapper ${mode==="register"?"slide":""}`}>

          {/* LOGIN */}

          <form className="auth-form" onSubmit={handleLogin}>

            <h2>Welcome back</h2>
            <p>Sign in to continue</p>

            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e)=>setEmail(e.target.value)}
            />

            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e)=>setPassword(e.target.value)}
            />

            <button>Sign In</button>

            <div className="switch">
              New to Valora?
              <span onClick={()=>setMode("register")}>
                Create an account
              </span>
            </div>

          </form>


          {/* REGISTER */}

          <form className="auth-form" onSubmit={handleRegister}>

            <h2>Create an account</h2>
            <p>Start building your knowledge base</p>

            <label>Full Name</label>
            <input
              type="text"
              value={name}
              onChange={(e)=>setName(e.target.value)}
            />

            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e)=>setEmail(e.target.value)}
            />

            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e)=>setPassword(e.target.value)}
            />

            <label>Confirm Password</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e)=>setConfirmPassword(e.target.value)}
            />

            <button>Create Account</button>

            <div className="switch">
              Already have an account?
              <span onClick={()=>setMode("login")}>
                Sign in
              </span>
            </div>

          </form>

        </div>

      </div>

    </div>
  )
}
