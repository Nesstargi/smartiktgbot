import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, test, vi } from "vitest";

import {
  createPromotion,
  getPromotions,
  updatePromotion,
} from "../api/promotions.api";
import PromotionsPage from "./PromotionsPage";

vi.mock("../api/promotions.api", () => ({
  getPromotions: vi.fn(),
  createPromotion: vi.fn(),
  updatePromotion: vi.fn(),
  deletePromotion: vi.fn(),
}));

describe("PromotionsPage", () => {
  test("allows inserting emoji into create promotion title", async () => {
    const user = userEvent.setup();

    getPromotions.mockResolvedValue({ items: [], total: 0 });
    createPromotion.mockResolvedValue({ id: 1, title: "🔥 Весенняя акция" });

    render(<PromotionsPage />);

    const titleInput = await screen.findByPlaceholderText("Название акции");
    await user.click(screen.getAllByRole("button", { name: "Эмодзи и подсказки" })[0]);
    await user.click(screen.getByRole("button", { name: "🔥" }));

    expect(titleInput).toHaveValue("🔥");
  });

  test("opens promotion edit dialog and saves changes", async () => {
    const user = userEvent.setup();

    getPromotions.mockResolvedValue({
      items: [
        {
          id: 10,
          title: "Супер акция",
          description: "Старая цена",
          image_url: null,
          is_active: true,
        },
      ],
      total: 1,
    });
    updatePromotion.mockResolvedValue({});

    render(<PromotionsPage />);

    const row = (await screen.findByText("Супер акция")).closest("tr");
    await user.click(within(row).getByRole("button", { name: "Изменить" }));

    const dialog = screen.getByRole("dialog", { name: "Редактировать акцию" });
    expect(dialog).toBeInTheDocument();

    const titleInput = within(dialog).getByPlaceholderText("Название акции");
    await user.clear(titleInput);
    await user.type(titleInput, "⚡ Супер акция");
    await user.click(within(dialog).getByRole("button", { name: "Сохранить акцию" }));

    await waitFor(() => {
      expect(updatePromotion).toHaveBeenCalledWith(10, {
        title: "⚡ Супер акция",
        description: "Старая цена",
      });
    });
  });
});
