import api from "./axios";

export const getStats = async () => {
  const res = await api.get("/admin/dashboard/stats");
  return res.data;
};
