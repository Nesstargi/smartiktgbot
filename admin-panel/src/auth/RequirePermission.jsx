import { Navigate } from "react-router-dom";

import { useAuth } from "./AuthContext";

export default function RequirePermission({ anyOf = [], allOf = [], children }) {
  const { loading, hasPermission, hasAllPermissions } = useAuth();

  if (loading) return <div>Loading...</div>;

  const anyOk = anyOf.length === 0 || anyOf.some((item) => hasPermission(item));
  const allOk = allOf.length === 0 || hasAllPermissions(allOf);

  if (!anyOk || !allOk) {
    return <Navigate to="/" replace />;
  }

  return children;
}
