import api, { toListResult } from "./axios";

export const getCategories = async (params = {}) => {
  const res = await api.get("/admin/categories/", { params });
  return toListResult(res);
};

export const createCategory = async (data) => {
  const res = await api.post("/admin/categories/", data);
  return res.data;
};

export const updateCategory = async (id, data) => {
  const res = await api.put(`/admin/categories/${id}`, data);
  return res.data;
};

export const deleteCategory = async (id) => {
  const res = await api.delete(`/admin/categories/${id}`);
  return res.data;
};
