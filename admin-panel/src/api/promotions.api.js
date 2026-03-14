import api, { toListResult } from "./axios";

export const getPromotions = async (params = {}) => {
  const res = await api.get("/admin/promotions/", { params });
  return toListResult(res);
};

export const createPromotion = async (data) => {
  const res = await api.post("/admin/promotions/", data);
  return res.data;
};

export const updatePromotion = async (id, data) => {
  const res = await api.put(`/admin/promotions/${id}`, data);
  return res.data;
};

export const deletePromotion = async (id) => {
  const res = await api.delete(`/admin/promotions/${id}`);
  return res.data;
};
