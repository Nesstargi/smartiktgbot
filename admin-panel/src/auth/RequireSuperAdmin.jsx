import { Navigate } from "react-router-dom";

import { useAuth } from "./AuthContext";

export default function RequireSuperAdmin({ children }) {
  const { loading, isSuperAdmin } = useAuth();

  if (loading) return <div>Loading...</div>;
  if (!isSuperAdmin) return <Navigate to="/" replace />;

  return children;
}
