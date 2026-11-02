import axios from "axios";

const API = "http://localhost:8080";

export const askAI = (chatId, message) =>
  axios.post(`${API}/ai/ask`, {
    chatId,
    content: message
  });