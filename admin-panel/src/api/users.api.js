import api, { toListResult } from "./axios";

export const getAdminUsers = async (params = {}) => {
  const res = await api.get("/admin/users/", { params });
  return toListResult(res);
};

export const getAvailablePermissions = async () => {
  const res = await api.get("/admin/users/permissions");
  return res.data.permissions || [];
};

export const createAdminUser = async (data) => {
  const res = await api.post("/admin/users/", data);
  return res.data;
};

export const updateAdminPermissions = async (userId, permissions) => {
  const res = await api.put(`/admin/users/${userId}/permissions`, { permissions });
  return res.data;
};

export const updateAdminRole = async (userId, isSuperAdmin) => {
  const res = await api.put(`/admin/users/${userId}/role`, { is_super_admin: isSuperAdmin });
  return res.data;
};

export const deleteAdminUser = async (userId) => {
  const res = await api.delete(`/admin/users/${userId}`);
  return res.data;
};
