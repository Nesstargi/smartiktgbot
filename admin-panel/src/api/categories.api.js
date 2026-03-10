import api from "./axios";

export const getCategories = async () => {
  const res = await api.get("/admin/categories/");
  return res.data;
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
