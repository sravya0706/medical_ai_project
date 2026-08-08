import { api } from "./api";

export async function getConversations() {
  const { data } = await api.get("/api/v1/history");
  return data.conversations || [];
}

export async function getConversation(conversationId) {
  const { data } = await api.get(`/api/v1/history/${conversationId}`);
  return data;
}
