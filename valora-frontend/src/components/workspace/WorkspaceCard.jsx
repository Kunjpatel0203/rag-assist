import { useNavigate } from "react-router-dom";

export default function WorkspaceCard({ workspace }) {

  const navigate = useNavigate();

  const getIcon = () => {

    const name = workspace.name.toLowerCase();

    if(name.includes("pdf")) return "📄";
    if(name.includes("excel")) return "📊";
    if(name.includes("code")) return "💻";
    if(name.includes("doc")) return "📚";

    return "🧠";
  };

  const openWorkspace = () => {
    navigate(`/workspace/${workspace.id}`);
  };

  return (

    <div
      className="workspace-card"
      onClick={openWorkspace}
      style={{cursor:"pointer"}}
    >

      <div className="workspace-card-icon">
        {getIcon()}
      </div>

      <h3>
        {workspace.name}
      </h3>

      <p className="workspace-description">
        AI knowledge workspace
      </p>

      <div className="workspace-footer">

        <span>Created</span>

        <span>
          {new Date(workspace.createdAt).toLocaleDateString()}
        </span>

      </div>

    </div>

  );
}