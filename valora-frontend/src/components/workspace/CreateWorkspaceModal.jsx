import { useState } from "react";
import { useNavigate } from "react-router-dom";
import FileDropzone from "./FileDropzone";
import WorkspacePreparing from "./WorkspacePreparing";

import "../../styles/workspaceModal.css";

import {
  createWorkspace,
  uploadFiles
} from "../../services/workspaceService";

export default function CreateWorkspaceModal({ close }) {

  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [files, setFiles] = useState([]);
  const [urls, setUrls] = useState([]);
  const [activeTab, setActiveTab] = useState("files");
  const [teamVisible, setTeamVisible] = useState(false);
  const [preparing, setPreparing] = useState(false);

  const addFiles = (newFiles) => {
    setFiles([...files, ...newFiles]);
  };

  const removeFile = (index) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const addUrl = () => {
    setUrls([...urls, ""]);
  };

  const updateUrl = (value, index) => {
    const copy = [...urls];
    copy[index] = value;
    setUrls(copy);
  };

  const removeUrl = (index) => {
    setUrls(urls.filter((_, i) => i !== index));
  };

const handleCreateWorkspace = async () => {

  if (!name) {
    alert("Workspace name required");
    return;
  }

  try {

    setPreparing(true);

    const token = localStorage.getItem("token");

    const workspace = await createWorkspace(name, token);

    if (files.length > 0) {
      await uploadFiles(workspace.id, files, token);
    }

    console.log("Upload finished");

    close();                 // close modal first
    navigate("/dashboard");  // then navigate

  } catch (err) {

    console.error(err);
    alert("Workspace creation failed");

  }

};

  // 🚀 Loader screen while embeddings generate
  if (preparing) {
    return <WorkspacePreparing />;
  }

  return (
    <div className="workspace-overlay">

      <div className="workspace-modal">

        <div className="workspace-scroll">

          {/* HEADER */}

          <div className="workspace-header">

            <div className="workspace-icon">🔒</div>

            <div>
              <h2>Create Workspace</h2>
              <p>Valora · AI-Powered</p>
            </div>

          </div>

          {/* WORKSPACE NAME */}

          <label className="workspace-label">
            WORKSPACE NAME
          </label>

          <input
            className="workspace-input"
            placeholder="e.g. Product Research Q2 2026"
            value={name}
            onChange={(e)=>setName(e.target.value)}
          />

          {/* DESCRIPTION */}

          <label className="workspace-label">
            DESCRIPTION — optional
          </label>

          <textarea
            className="workspace-textarea"
            placeholder="What is this workspace for?"
            value={description}
            onChange={(e)=>setDescription(e.target.value)}
          />

          {/* SOURCE TABS */}

          <label className="workspace-label">
            ADD SOURCES
          </label>

          <div className="source-tabs">

            <button
              className={activeTab==="files" ? "active" : ""}
              onClick={()=>setActiveTab("files")}
            >
              Files
            </button>

            <button
              className={activeTab==="urls" ? "active" : ""}
              onClick={()=>setActiveTab("urls")}
            >
              URLs
            </button>

          </div>

          {/* FILE UPLOAD */}

          {activeTab==="files" && (
            <>
              <FileDropzone addFiles={addFiles}/>

              <div className="file-list">

                {files.map((file,index)=>(
                  <div key={index} className="file-item">

                    <span className="file-dot"></span>

                    <span className="file-name">
                      {file.name}
                    </span>

                    <span
                      className="file-remove"
                      onClick={()=>removeFile(index)}
                    >
                      ✕
                    </span>

                  </div>
                ))}

              </div>
            </>
          )}

          {/* URL INPUT */}

          {activeTab==="urls" && (
            <div className="url-container">

              {urls.map((url,index)=>(
                <div key={index} className="url-item">

                  <input
                    placeholder="https://example.com"
                    value={url}
                    onChange={(e)=>updateUrl(e.target.value,index)}
                  />

                  <button
                    onClick={()=>removeUrl(index)}
                  >
                    ✕
                  </button>

                </div>
              ))}

              <button
                className="add-url"
                onClick={addUrl}
              >
                + Add URL
              </button>

            </div>
          )}

          {/* TEAM VISIBILITY */}

          <div className="team-toggle">

            <span>
              Make workspace visible to team
            </span>

            <label className="switch">

              <input
                type="checkbox"
                checked={teamVisible}
                onChange={()=>setTeamVisible(!teamVisible)}
              />

              <span className="slider"></span>

            </label>

          </div>

        </div>

        {/* ACTION BUTTONS */}

        <div className="workspace-actions">

          <button
            className="cancel-btn"
            onClick={close}
          >
            Cancel
          </button>

          <button
            className="create-btn"
            onClick={handleCreateWorkspace}
          >
            + Create Workspace
          </button>

        </div>

      </div>

    </div>
  );
}