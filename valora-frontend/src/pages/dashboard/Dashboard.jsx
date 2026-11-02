import { useEffect, useState } from "react";
import Sidebar from "../../components/workspace/Sidebar";
import WorkspaceCard from "../../components/workspace/WorkspaceCard";
import CreateWorkspaceModal from "../../components/workspace/CreateWorkspaceModal";
import WorkspaceSkeleton from "../../components/workspace/WorkspaceSkeleton";

import "../../styles/dashboard.css";

export default function Dashboard() {

  const [workspaces, setWorkspaces] = useState([]);
  const [search, setSearch] = useState("");
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    fetchWorkspaces();
  }, []);

  const fetchWorkspaces = async () => {

    try {

      const token = localStorage.getItem("token");

      const res = await fetch("http://localhost:8080/workspace/my", {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      const data = await res.json();

      setWorkspaces(data);

    } catch (err) {
      console.error(err);
    }

  };

  const filtered = workspaces.filter((w) =>
    w.name.toLowerCase().includes(search.toLowerCase())
  );

  return (

    <div className="dashboard">

      <Sidebar />

      <div className="dashboard-main">

        <div className="dashboard-header">

          <h1>Hi 👋</h1>
          <p>Manage your AI knowledge workspaces</p>

        </div>

        <input
          className="workspace-search"
          placeholder="Search workspaces..."
          value={search}
          onChange={(e)=>setSearch(e.target.value)}
        />

        <div className="workspace-grid">

  {workspaces.length === 0
    ? [...Array(6)].map((_,i)=>(
        <WorkspaceSkeleton key={i}/>
      ))
    : filtered.map((ws)=>(
        <WorkspaceCard key={ws.id} workspace={ws}/>
      ))
  }

  <div
    className="new-workspace-card"
    onClick={()=>setShowModal(true)}
  >
    + New Workspace
  </div>

</div>

      </div>

      {/* CREATE WORKSPACE MODAL */}

      {showModal && (
        <CreateWorkspaceModal
          close={()=>setShowModal(false)}
        />
      )}

    </div>

  );
}