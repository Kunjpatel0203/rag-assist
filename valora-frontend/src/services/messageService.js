import axios from "axios";

const API = "http://localhost:8080";

const token = localStorage.getItem("token");

const authHeader = {
  headers: {
    Authorization: `Bearer ${token}`
  }
};

export const getMessages = (chatId) =>
  axios.get(`${API}/message/chat/${chatId}`, authHeader);

export const askAI = (chatId, content) =>
  axios.post(
    `${API}/ai/ask`,
    {
      chatId: chatId,
      content: content
    },
    authHeader
  );