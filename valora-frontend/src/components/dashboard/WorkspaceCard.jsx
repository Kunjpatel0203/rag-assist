export default function WorkspaceCard({workspace}){

  return(

    <div className="workspace-card">

      <div className="workspace-icon">
        📁
      </div>

      <h3>{workspace.name}</h3>

      <p>
        Created {workspace.createdAt}
      </p>

    </div>

  );

}