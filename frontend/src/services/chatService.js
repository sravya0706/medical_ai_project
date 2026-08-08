import { api } from "./api";

export async function sendMessage(message, sessionId) {
  const { data } = await api.post("/api/v1/chat", {
    message,
    session_id: sessionId,
  });
  return data;
}

export async function sendImage(file, message, sessionId) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("message", message);
  formData.append("session_id", sessionId);

  const { data } = await api.post("/api/v1/vision/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}
