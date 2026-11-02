import { useState } from "react";
import { uploadDocuments } from "../../services/documentService";

export default function UploadDocument({ workspaceId, refreshDocs }) {

  const [files, setFiles] = useState([]);

  const handleDrop = (e) => {
    e.preventDefault();
    setFiles(e.dataTransfer.files);
  };

  const handleUpload = async () => {
    await uploadDocuments(workspaceId, files);
    refreshDocs();
  };

  return (

    <div
      className="upload-box"
      onDragOver={(e)=>e.preventDefault()}
      onDrop={handleDrop}
    >

      Drag & Drop files here

      <input
        type="file"
        multiple
        onChange={(e)=>setFiles(e.target.files)}
      />

      <button onClick={handleUpload}>
        Upload
      </button>

    </div>

  );
}