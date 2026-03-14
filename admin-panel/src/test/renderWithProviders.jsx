import { render } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { vi } from "vitest";

import AuthContext from "../auth/AuthContext";

export function createAuthValue(overrides = {}) {
  const permissions = overrides.permissions ?? [];
  const roles = overrides.roles ?? [];
  const isSuperAdmin = overrides.isSuperAdmin ?? roles.includes("super_admin");

  return {
    token: overrides.token ?? "test-token",
    user: overrides.user ?? null,
    loading: overrides.loading ?? false,
    login: overrides.login ?? vi.fn(),
    logout: overrides.logout ?? vi.fn(),
    isAuth: overrides.isAuth ?? true,
    permissions,
    roles,
    isSuperAdmin,
    hasPermission:
      overrides.hasPermission
      ?? ((permission) => isSuperAdmin || permissions.includes(permission)),
    hasAllPermissions:
      overrides.hasAllPermissions
      ?? ((required) => isSuperAdmin || required.every((permission) => permissions.includes(permission))),
  };
}

export function renderWithProviders(
  ui,
  {
    route = "/",
    auth: authOverrides = {},
  } = {},
) {
  const auth = createAuthValue(authOverrides);

  return {
    auth,
    ...render(
      <MemoryRouter initialEntries={[route]}>
        <AuthContext.Provider value={auth}>{ui}</AuthContext.Provider>
      </MemoryRouter>,
    ),
  };
}
