import api, { toListResult } from "./axios";

export const getLeads = async (params = {}) => {
  const res = await api.get("/admin/leads/", { params });
  return toListResult(res);
};

export const deleteLead = async (id) => {
  const res = await api.delete(`/admin/leads/${id}`);
  return res.data;
};
