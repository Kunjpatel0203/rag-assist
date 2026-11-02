import axios from "axios";

const API = "http://localhost:8080/auth";

export const loginUser = async (data) => {
  const res = await axios.post(`${API}/login`, data);
  return res.data;
};

export const registerUser = async (data) => {
  const res = await axios.post(`${API}/register`, data);
  return res.data;
};

export const forgotPassword = async (email) => {
  const res = await axios.post(`${API}/forgot-password?email=${email}`);
  return res.data;
};

export const resetPassword = async (data) => {
  const res = await axios.post(`${API}/reset-password`, data);
  return res.data;
};

export const resendVerification = async (email) => {
  const res = await axios.post(`${API}/resend-verification?email=${email}`);
  return res.data;
};