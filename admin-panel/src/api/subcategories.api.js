import api, { toListResult } from "./axios";

export async function getSubcategoriesByCategory(categoryId) {
  const res = await api.get(`/api/subcategories/${categoryId}`);
  return res.data;
}

export async function getAllSubcategories(params = {}) {
  const res = await api.get("/admin/subcategories/", { params });
  return toListResult(res);
}

export async function createSubcategory(data) {
  const res = await api.post("/admin/subcategories/", data);
  return res.data;
}

export async function updateSubcategory(id, data) {
  const res = await api.put(`/admin/subcategories/${id}`, data);
  return res.data;
}

export async function deleteSubcategory(id) {
  const res = await api.delete(`/admin/subcategories/${id}`);
  return res.data;
}
