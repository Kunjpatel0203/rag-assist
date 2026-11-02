import "../../styles/workspacePreparing.css";

export default function WorkspacePreparing() {

  return (
    <div className="workspace-preparing">

      <div className="rocket">🚀</div>

      <h2>Preparing your workspace</h2>

      <p>
        Uploading documents and generating embeddings.
        This may take a few seconds.
      </p>

      <div className="progress-container">
        <div className="progress-bar"></div>
      </div>

      <div className="steps">

        <div className="step">📄 Uploading files</div>

        <div className="step">🧠 Generating embeddings</div>

        <div className="step">📊 Indexing vectors</div>

      </div>

    </div>
  );
}