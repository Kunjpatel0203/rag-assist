const API="http://localhost:8080/workspace";

export const createWorkspace = async (name,token)=>{

const res = await fetch(`${API}/create`,{
method:"POST",
headers:{
"Content-Type":"application/json",
Authorization:`Bearer ${token}`
},
body:JSON.stringify({name})
});

return res.json();
};
export const uploadFiles = async (workspaceId, files, token) => {

  const formData = new FormData();

  files.forEach(file => {
    formData.append("files", file);
  });

  const res = await fetch(
    `http://localhost:8080/workspace/${workspaceId}/upload`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`
      },
      body: formData
    }
  );

  const text = await res.text();

  console.log("Upload response:", text);

  return text;
};