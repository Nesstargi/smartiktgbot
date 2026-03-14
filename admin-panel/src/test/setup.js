import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach, beforeEach, vi } from "vitest";

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

beforeEach(() => {
  localStorage.clear();
  vi.stubGlobal("confirm", vi.fn(() => true));
});
