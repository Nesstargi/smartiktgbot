import api from "./axios";

export const broadcastNotification = async (data) => {
  const res = await api.post("/admin/notifications/broadcast", data);
  return res.data;
};
