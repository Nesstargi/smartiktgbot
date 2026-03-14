import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, test, vi } from "vitest";

import { getStats } from "../api/dashboard.api";
import Dashboard from "./Dashboard";

vi.mock("../api/dashboard.api", () => ({
  getStats: vi.fn(),
}));

describe("Dashboard", () => {
  test("loads and refreshes dashboard metrics", async () => {
    const user = userEvent.setup();

    getStats
      .mockResolvedValueOnce({
        categories: 2,
        subcategories: 5,
        products: 12,
        promotions: 1,
        leads: 4,
      })
      .mockResolvedValueOnce({
        categories: 3,
        subcategories: 6,
        products: 14,
        promotions: 2,
        leads: 7,
      });

    render(<Dashboard />);

    expect(await screen.findByText("12")).toBeInTheDocument();
    expect(screen.getByText("Сводка по текущему состоянию каталога, акций и входящих заявок.")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Обновить" }));

    await waitFor(() => {
      expect(getStats).toHaveBeenCalledTimes(2);
    });
    expect(await screen.findByText("14")).toBeInTheDocument();
  });
});
