import { createContext, useContext, useEffect, useMemo, useState } from "react";

import api from "../api/axios";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const savedToken = localStorage.getItem("access_token");

      if (!savedToken) {
        setLoading(false);
        return;
      }

      localStorage.setItem("access_token", savedToken);
      try {
        const me = await api.get("/admin/auth/me");
        setToken(savedToken);
        setUser(me.data);
      } catch {
        localStorage.removeItem("access_token");
        localStorage.removeItem("auth_user");
        setToken(null);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = (newToken, userPayload) => {
    localStorage.setItem("access_token", newToken);
    if (userPayload) {
      localStorage.setItem("auth_user", JSON.stringify(userPayload));
      setUser(userPayload);
    }
    setToken(newToken);
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("auth_user");
    setToken(null);
    setUser(null);
  };

  const permissions = user?.permissions || [];
  const roles = user?.roles || [];
  const isSuperAdmin = roles.includes("super_admin");

  const value = useMemo(
    () => ({
      token,
      user,
      loading,
      login,
      logout,
      isAuth: !!token,
      permissions,
      roles,
      isSuperAdmin,
      hasPermission: (perm) => isSuperAdmin || permissions.includes(perm),
      hasAllPermissions: (perms) => isSuperAdmin || perms.every((p) => permissions.includes(p)),
    }),
    [token, user, loading, permissions, roles, isSuperAdmin],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
