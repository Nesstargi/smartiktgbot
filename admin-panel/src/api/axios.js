import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export function toListResult(response) {
  const items = Array.isArray(response.data) ? response.data : [];
  const rawTotal = response.headers?.["x-total-count"];
  const parsedTotal = Number.parseInt(rawTotal ?? "", 10);

  return {
    items,
    total: Number.isNaN(parsedTotal) ? items.length : parsedTotal,
  };
}

export function getApiErrorMessage(error, fallback = "Не удалось выполнить запрос") {
  const detail = error?.response?.data?.detail;

  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => {
        if (typeof item === "string") return item;
        return item?.msg;
      })
      .filter(Boolean);

    if (messages.length) return messages.join(", ");
    return "Ошибка валидации";
  }

  if (typeof detail === "string" && detail.trim()) {
    return detail;
  }

  if (error?.message) {
    return error.message;
  }

  return fallback;
}

export default api;
