export default function SourceBlock({block,index,update,remove}){

  const allowedTypes = {
    PDF:["pdf"],
    DOC:["doc","docx"],
    PPT:["ppt","pptx"],
    XLS:["xls","xlsx","csv"],
    CODE:["py","java","js","ts","cpp","c","cs","go","html","css","json","xml"]
  };

  const handleFile = (e)=>{

    const file = e.target.files[0];

    const ext = file.name.split(".").pop();

    if(!allowedTypes[block.type]?.includes(ext)){
      alert("Invalid file type for "+block.type);
      return;
    }

    update(index,{
      ...block,
      file:file
    });

  };

  return(

    <div className="source-block">

      <div className="block-header">
        Source {index+1}
        <span
          onClick={()=>remove(index)}
        >
          ❌
        </span>
      </div>

      <select
        value={block.type}
        onChange={(e)=>update(index,{
          ...block,
          type:e.target.value
        })}
      >

        <option value="">Select Type</option>
        <option value="PDF">PDF</option>
        <option value="DOC">DOC</option>
        <option value="PPT">PPT</option>
        <option value="XLS">XLS</option>
        <option value="CODE">CODE</option>
        <option value="URL">URL</option>

      </select>

      {block.type==="URL" ? (

        <input
          placeholder="Enter URL"
          value={block.url || ""}
          onChange={(e)=>update(index,{
            ...block,
            url:e.target.value
          })}
        />

      ): block.type && (

        <input
          type="file"
          onChange={handleFile}
        />

      )}

    </div>

  );

}