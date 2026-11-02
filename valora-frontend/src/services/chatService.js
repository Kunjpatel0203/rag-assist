import axios from "axios";

const API = "http://localhost:8080";

function authHeader() {

  const token = localStorage.getItem("token");

  return {
    headers: {
      Authorization: `Bearer ${token}`
    }
  };
}

export const getChats = (workspaceId) =>
  axios.get(`${API}/chat/workspace/${workspaceId}`, authHeader());

export const createChat = (workspaceId) =>
  axios.post(
    `${API}/chat/create`,
    {
      workspaceId,
      title: "New Chat"
    },
    authHeader()
  );