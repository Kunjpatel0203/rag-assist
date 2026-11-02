import { useEffect, useState } from "react";
import {
  getDocuments,
  deleteDocument,
  openDocument,
  uploadDocuments
} from "../../services/documentService";

export default function DocumentPanel({ workspaceId }) {

  const [documents, setDocuments] = useState([]);
  const [files, setFiles] = useState([]);

  useEffect(() => {
    loadDocs();
  }, [workspaceId]);

  const loadDocs = async () => {

    const res = await getDocuments(workspaceId);

    setDocuments(res.data.documents || []);

  };

  const handleDelete = async (blockId) => {

    await deleteDocument(workspaceId, blockId);

    loadDocs();

  };

  const handleUpload = async () => {

    if (!files.length) return;

    await uploadDocuments(workspaceId, files);

    setFiles([]);

    loadDocs();

  };

  return (

    <div className="documents-wrapper">

      <h3 className="documents-title">Documents</h3>

      {/* Upload Box */}

      <div className="upload-box">

        <input
          type="file"
          multiple
          onChange={(e)=>setFiles(e.target.files)}
        />

        <button
          className="upload-btn"
          onClick={handleUpload}
        >
          Upload
        </button>

      </div>

      {/* Document List */}

      <div className="documents-list">

        {documents.map(doc => (

          <div key={doc.block_id} className="doc-card">

            <div className="doc-left">

              <div className="doc-icon">📄</div>

              <div className="doc-info">

                <div className="doc-name">
                  {doc.name}
                </div>

                <div className="doc-type">
                  {doc.type}
                </div>

              </div>

            </div>

            <div className="doc-actions">

              <button
                className="doc-btn"
                onClick={() =>
                  window.open(
                    openDocument(workspaceId, doc.block_id)
                  )
                }
              >
                View
              </button>

              <button
                className="doc-btn delete"
                onClick={()=>handleDelete(doc.block_id)}
              >
                Delete
              </button>

            </div>

          </div>

        ))}

      </div>

    </div>

  );

}