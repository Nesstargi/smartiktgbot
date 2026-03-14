import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, test, vi } from "vitest";

import api from "../api/axios";
import { AuthProvider } from "./AuthProvider";
import { useAuth } from "./AuthContext";

vi.mock("../api/axios", () => ({
  default: {
    get: vi.fn(),
  },
}));

function AuthProbe() {
  const auth = useAuth();

  if (auth.loading) {
    return <div>loading</div>;
  }

  return <div>{auth.isAuth ? auth.user?.email : "guest"}</div>;
}

describe("AuthProvider", () => {
  test("restores authenticated user from saved token", async () => {
    localStorage.setItem("access_token", "saved-token");
    api.get.mockResolvedValue({
      data: {
        email: "boss@example.com",
        permissions: ["manage_notifications"],
        roles: ["admin", "super_admin"],
      },
    });

    render(
      <AuthProvider>
        <AuthProbe />
      </AuthProvider>,
    );

    expect(await screen.findByText("boss@example.com")).toBeInTheDocument();
    expect(api.get).toHaveBeenCalledWith("/admin/auth/me");
  });

  test("drops invalid saved token and becomes guest", async () => {
    localStorage.setItem("access_token", "broken-token");
    api.get.mockRejectedValue(new Error("Unauthorized"));

    render(
      <AuthProvider>
        <AuthProbe />
      </AuthProvider>,
    );

    await waitFor(() => {
      expect(screen.getByText("guest")).toBeInTheDocument();
    });
    expect(localStorage.getItem("access_token")).toBeNull();
  });
});
