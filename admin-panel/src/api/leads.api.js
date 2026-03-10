import api from "./axios";

export const getLeads = async () => {
  const res = await api.get("/admin/leads/");
  return res.data;
};

export const deleteLead = async (id) => {
  const res = await api.delete(`/admin/leads/${id}`);
  return res.data;
};
