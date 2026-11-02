import { useState } from "react";
import SourceBlock from "./SourceBlock";
import RocketLoader from "../ui/RocketLoader";
import "../../styles/workspaceModal.css";

export default function CreateWorkspaceModal({close}){

  const [name,setName] = useState("");
  const [sources,setSources] = useState([]);
  const [processing,setProcessing] = useState(false);

  const addSource = ()=>{
    setSources([...sources,{
      type:"",
      file:null
    }]);
  };

  const updateSource = (i,data)=>{
    const newSources=[...sources];
    newSources[i]=data;
    setSources(newSources);
  };

  const removeSource = (i)=>{
    setSources(sources.filter((_,index)=>index!==i));
  };

  const handleCreate = ()=>{

    setProcessing(true);

    setTimeout(()=>{
      setProcessing(false);
      close();
    },3000);

  };

  if(processing){
    return <RocketLoader/>
  }

  return(

    <div className="modal-overlay">

      <div className="modal">

        <h2>Create Workspace</h2>

        <input
          placeholder="Workspace name"
          value={name}
          onChange={(e)=>setName(e.target.value)}
        />

        <div className="sources">

          {sources.map((block,i)=>(
            <SourceBlock
              key={i}
              index={i}
              block={block}
              update={updateSource}
              remove={removeSource}
            />
          ))}

        </div>

        <button
          className="add-source"
          onClick={addSource}
        >
          + Add Source
        </button>

        <div className="modal-actions">

          <button onClick={close}>
            Cancel
          </button>

          <button
            className="create-btn"
            onClick={handleCreate}
          >
            Create Workspace
          </button>

        </div>

      </div>

    </div>

  );

}