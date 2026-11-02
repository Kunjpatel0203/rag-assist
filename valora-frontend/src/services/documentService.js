import axios from "axios";

const API = "http://localhost:8000";

export const getDocuments = (workspaceId) =>
  axios.get(`${API}/documents/${workspaceId}`);

export const deleteDocument = (workspaceId, blockId) =>
  axios.delete(`${API}/documents/${workspaceId}/${blockId}`);

export const openDocument = (workspaceId, blockId) =>
  `${API}/documents/${workspaceId}/${blockId}/open`;

export const uploadDocuments = (workspaceId, files) => {

  const form = new FormData();

  form.append("workspace_id", workspaceId);

  for (let f of files) {
    form.append("files", f);
  }

  return axios.post(`${API}/ingest`, form);

};