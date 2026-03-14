import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, test, vi } from "vitest";

import { broadcastNotification } from "../api/notifications.api";
import NotificationsPage from "./NotificationsPage";

vi.mock("../api/notifications.api", () => ({
  broadcastNotification: vi.fn(),
}));

describe("NotificationsPage", () => {
  test("submits broadcast and shows result summary", async () => {
    const user = userEvent.setup();

    broadcastNotification.mockResolvedValue({
      total: 8,
      success: 7,
      failed: 1,
    });

    render(<NotificationsPage />);

    await user.type(screen.getByPlaceholderText("Заголовок"), "Весеннее обновление");
    await user.type(screen.getByPlaceholderText("Текст уведомления"), "Новые товары уже в каталоге");

    expect(screen.getByText("Весеннее обновление")).toBeInTheDocument();
    expect(screen.getByDisplayValue("Новые товары уже в каталоге")).toBeInTheDocument();
    expect(screen.getAllByText("Новые товары уже в каталоге")).toHaveLength(2);

    await user.click(screen.getByRole("button", { name: "Отправить уведомление" }));

    await waitFor(() => {
      expect(broadcastNotification).toHaveBeenCalledWith({
        title: "Весеннее обновление",
        message: "Новые товары уже в каталоге",
        image_url: null,
      });
    });
    expect(await screen.findByText("Результат рассылки")).toBeInTheDocument();
    expect(screen.getByText("Рассылка завершена частично: часть сообщений ушла успешно, часть нет.")).toBeInTheDocument();
  });

  test("shows api error when sending fails", async () => {
    const user = userEvent.setup();

    broadcastNotification.mockRejectedValue({
      response: {
        data: {
          detail: "Notification service is not configured",
        },
      },
    });

    render(<NotificationsPage />);

    await user.type(screen.getByPlaceholderText("Заголовок"), "Сервис недоступен");
    await user.type(screen.getByPlaceholderText("Текст уведомления"), "Пробуем отправить");
    await user.click(screen.getByRole("button", { name: "Отправить уведомление" }));

    expect(await screen.findByText("Notification service is not configured")).toBeInTheDocument();
  });
});
