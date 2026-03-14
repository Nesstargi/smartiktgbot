import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Route, Routes } from "react-router-dom";
import { describe, expect, test, vi } from "vitest";

import api from "../api/axios";
import Login from "./Login";
import { renderWithProviders } from "../test/renderWithProviders";

vi.mock("../api/axios", () => ({
  default: {
    post: vi.fn(),
  },
}));

describe("Login page", () => {
  test("logs in and redirects to dashboard on success", async () => {
    const user = userEvent.setup();
    const loginSpy = vi.fn();

    api.post.mockResolvedValue({
      data: {
        access_token: "token-123",
        user: {
          email: "admin@example.com",
          permissions: ["manage_products"],
          roles: ["admin"],
        },
      },
    });

    renderWithProviders(
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<div>dashboard-home</div>} />
      </Routes>,
      {
        route: "/login",
        auth: {
          login: loginSpy,
        },
      },
    );

    await user.type(screen.getByPlaceholderText("Email"), "admin@example.com");
    await user.type(screen.getByPlaceholderText("Password"), "secret123");
    await user.click(screen.getByRole("button", { name: "Войти" }));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith("/admin/auth/login", {
        email: "admin@example.com",
        password: "secret123",
      });
    });
    expect(loginSpy).toHaveBeenCalledWith("token-123", {
      email: "admin@example.com",
      permissions: ["manage_products"],
      roles: ["admin"],
    });
    expect(await screen.findByText("dashboard-home")).toBeInTheDocument();
  });

  test("shows friendly error when credentials are invalid", async () => {
    const user = userEvent.setup();
    api.post.mockRejectedValue(new Error("Unauthorized"));

    renderWithProviders(<Login />, {
      route: "/login",
      auth: {
        login: vi.fn(),
      },
    });

    await user.type(screen.getByPlaceholderText("Email"), "wrong@example.com");
    await user.type(screen.getByPlaceholderText("Password"), "wrongpass");
    await user.click(screen.getByRole("button", { name: "Войти" }));

    expect(await screen.findByText("Неверный email или пароль")).toBeInTheDocument();
  });
});
