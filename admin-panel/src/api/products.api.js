import api, { toListResult } from "./axios";

export const getProducts = async (params = {}) => {
  const res = await api.get("/admin/products/", { params });
  return toListResult(res);
};

export const createProduct = async (data) => {
  const res = await api.post("/admin/products/", data);
  return res.data;
};

export const updateProduct = async (id, data) => {
  const res = await api.put(`/admin/products/${id}`, data);
  return res.data;
};

export const deleteProduct = async (id) => {
  const res = await api.delete(`/admin/products/${id}`);
  return res.data;
};
