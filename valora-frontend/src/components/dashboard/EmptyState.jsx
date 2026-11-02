export default function EmptyState({openModal}){

  return(

    <div className="empty-state">

      <div className="empty-icon">🚀</div>

      <h2>Start Your Knowledge Journey</h2>

      <p>Create your first workspace to begin uploading documents.</p>

      <button
        className="create-btn"
        onClick={openModal}
      >
        Create Workspace
      </button>

    </div>

  );
}