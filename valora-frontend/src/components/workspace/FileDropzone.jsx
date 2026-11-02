import { useRef } from "react";

export default function FileDropzone({ addFiles }) {

  const inputRef = useRef();

  const handleFiles = (files) => {

    const allowed = [
      "pdf","doc","docx",
      "ppt","pptx",
      "xls","xlsx","csv",
      "py","java","js","ts",
      "cpp","c","cs","go",
      "html","css","json","xml",
      "txt","md"
    ];

    const valid = [];

    for(let f of files){

      const ext = f.name.split(".").pop();

      if(allowed.includes(ext)){
        valid.push(f);
      }else{
        alert("Unsupported file type: "+ext);
      }

    }

    addFiles(valid);

  };

  const drop = (e) => {
    e.preventDefault();
    handleFiles(e.dataTransfer.files);
  };

  return (

    <div
      className="file-dropzone"
      onDragOver={(e)=>e.preventDefault()}
      onDrop={drop}
      onClick={()=>inputRef.current.click()}
    >

      <div className="upload-icon">
        ⬆
      </div>

      <p>
        Drop files here or <span>browse</span>
      </p>

      <small>
        Drag and drop multiple files
      </small>

      <div className="supported">
        PDF DOCX XLSX TXT MD CSV PPTX
      </div>

      <input
        type="file"
        multiple
        ref={inputRef}
        style={{display:"none"}}
        onChange={(e)=>handleFiles(e.target.files)}
      />

    </div>

  );
}