import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, test, vi } from "vitest";

import { createCategory } from "../api/categories.api";
import { getCategories } from "../api/categories.api";
import { getProducts, updateProduct } from "../api/products.api";
import { getAllSubcategories } from "../api/subcategories.api";
import CatalogPage from "./CatalogPage";

vi.mock("../api/categories.api", () => ({
  getCategories: vi.fn(),
  createCategory: vi.fn(),
  updateCategory: vi.fn(),
  deleteCategory: vi.fn(),
}));

vi.mock("../api/subcategories.api", () => ({
  getAllSubcategories: vi.fn(),
  createSubcategory: vi.fn(),
  updateSubcategory: vi.fn(),
  deleteSubcategory: vi.fn(),
}));

vi.mock("../api/products.api", () => ({
  getProducts: vi.fn(),
  createProduct: vi.fn(),
  updateProduct: vi.fn(),
  deleteProduct: vi.fn(),
}));

describe("CatalogPage", () => {
  test("loads categories, subcategories and products", async () => {
    getCategories.mockImplementation(async (params = {}) => ({
      items: params.limit
        ? [{ id: 1, name: "Телефоны" }]
        : [
            { id: 1, name: "Телефоны" },
            { id: 2, name: "Ноутбуки" },
          ],
      total: params.limit ? 1 : 2,
    }));

    getAllSubcategories.mockImplementation(async (params = {}) => ({
      items: params.limit
        ? [{ id: 10, name: "Android", category_id: 1, image_url: null }]
        : [
            { id: 10, name: "Android", category_id: 1, image_url: null },
            { id: 11, name: "Ultrabooks", category_id: 2, image_url: null },
          ],
      total: params.limit ? 1 : 2,
    }));

    getProducts.mockResolvedValue({
      items: [
        {
          id: 101,
          name: "Galaxy A55",
          description: "Средний сегмент",
          subcategory_id: 10,
          image_file_id: "",
        },
      ],
      total: 1,
    });

    render(<CatalogPage />);

    expect(await screen.findByText("Galaxy A55")).toBeInTheDocument();
    expect(screen.getByText("Android")).toBeInTheDocument();
    expect(screen.getAllByText("Телефоны").length).toBeGreaterThan(0);

    await waitFor(() => {
      expect(getCategories).toHaveBeenCalled();
      expect(getAllSubcategories).toHaveBeenCalled();
      expect(getProducts).toHaveBeenCalledWith({
        q: undefined,
        subcategory_id: undefined,
        limit: 10,
        offset: 0,
      });
    });
  });

  test("allows inserting emoji into create category field", async () => {
    const user = userEvent.setup();

    getCategories.mockImplementation(async (params = {}) => ({
      items: params.limit ? [] : [],
      total: 0,
    }));
    getAllSubcategories.mockImplementation(async (params = {}) => ({
      items: params.limit ? [] : [],
      total: 0,
    }));
    getProducts.mockResolvedValue({ items: [], total: 0 });
    createCategory.mockResolvedValue({ id: 1, name: "📱 Телефоны" });

    render(<CatalogPage />);

    const categoryInput = await screen.findByPlaceholderText("Новая категория");
    await user.click(screen.getAllByRole("button", { name: "Эмодзи и фразы" })[0]);
    await user.click(screen.getByRole("button", { name: "📱" }));

    expect(categoryInput).toHaveValue("📱");
  });

  test("opens product edit dialog and saves changes", async () => {
    const user = userEvent.setup();

    getCategories.mockImplementation(async (params = {}) => ({
      items: params.limit
        ? [{ id: 1, name: "Телефоны" }]
        : [{ id: 1, name: "Телефоны" }],
      total: 1,
    }));

    getAllSubcategories.mockImplementation(async (params = {}) => ({
      items: params.limit
        ? [{ id: 10, name: "Android", category_id: 1, image_url: null }]
        : [{ id: 10, name: "Android", category_id: 1, image_url: null }],
      total: 1,
    }));

    getProducts.mockResolvedValue({
      items: [
        {
          id: 101,
          name: "Galaxy A55",
          description: "Средний сегмент",
          subcategory_id: 10,
          image_file_id: "",
        },
      ],
      total: 1,
    });
    updateProduct.mockResolvedValue({});

    render(<CatalogPage />);

    const row = (await screen.findByText("Galaxy A55")).closest("tr");
    await user.click(within(row).getByRole("button", { name: "Изменить" }));

    expect(screen.getByRole("dialog", { name: "Редактировать товар" })).toBeInTheDocument();

    const nameInput = screen.getByPlaceholderText("Название товара");
    await user.clear(nameInput);
    await user.type(nameInput, "Galaxy A56");
    await user.click(screen.getByRole("button", { name: "Сохранить товар" }));

    await waitFor(() => {
      expect(updateProduct).toHaveBeenCalledWith(101, {
        name: "Galaxy A56",
        description: "Средний сегмент",
      });
    });
  });
});
