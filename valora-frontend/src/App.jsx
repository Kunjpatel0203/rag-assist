import { BrowserRouter, Routes, Route } from "react-router-dom";

import Landing from "./pages/Landing";

import Auth from "./pages/auth/Auth";
import ForgotPassword from "./pages/auth/ForgotPassword";
import ResetPassword from "./pages/auth/ResetPassword";
import Dashboard from "./pages/dashboard/Dashboard";
import WorkspacePage from "./pages/WorkspacePage";

function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* LANDING PAGE */}
        <Route path="/" element={<Landing />} />

        {/* AUTH */}
        <Route path="/login" element={<Auth />} />
        <Route path="/auth" element={<Auth />} />

        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />

        {/* APP */}
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/workspace/:workspaceId" element={<WorkspacePage />} />

      </Routes>
    </BrowserRouter>
  );
}

export default App;