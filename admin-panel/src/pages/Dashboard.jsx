import { useEffect, useState } from "react";

import { getApiErrorMessage } from "../api/axios";
import { getStats } from "../api/dashboard.api";

const primaryItems = [
  { key: "categories", label: "Категории", hint: "Верхний уровень каталога" },
  { key: "subcategories", label: "Подкатегории", hint: "Разделы внутри категорий" },
  { key: "products", label: "Товары", hint: "Позиции, доступные в каталоге" },
  { key: "promotions", label: "Акции", hint: "Маркетинговые предложения" },
  { key: "leads", label: "Заявки", hint: "Контакты и запросы клиентов" },
  { key: "bot_users", label: "Пользователи бота", hint: "Все пользователи, попавшие в аудиторию рассылки" },
];

function formatDateTime(value) {
  if (!value) return "еще не обновлялось";
  return value.toLocaleString("ru-RU", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export default function Dashboard() {
  const [stats, setStats] = useState({
    categories: 0,
    subcategories: 0,
    products: 0,
    promotions: 0,
    leads: 0,
    bot_users: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);

  const loadStats = async ({ silent = false } = {}) => {
    if (silent) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }

    setError("");
    try {
      const data = await getStats();
      setStats(data);
      setLastUpdated(new Date());
    } catch (loadError) {
      setError(getApiErrorMessage(loadError, "Не удалось загрузить дашборд"));
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadStats();
  }, []);

  return (
    <section>
      <div className="stats-header">
        <div>
          <h2 className="page-title">Дашборд</h2>
          <p className="muted">Сводка по текущему состоянию каталога, акций и входящих заявок.</p>
        </div>
        <div className="inline-actions">
          <p className="muted">Обновлено: {formatDateTime(lastUpdated)}</p>
          <button type="button" onClick={() => loadStats({ silent: true })} disabled={loading || refreshing}>
            {refreshing ? "Обновляем..." : "Обновить"}
          </button>
        </div>
      </div>

      {error && <p className="error-text">{error}</p>}

      {loading ? (
        <p className="muted">Загрузка дашборда...</p>
      ) : (
        <div className="stats-grid">
          {primaryItems.map((item) => (
            <article className="card metric-card" key={item.key}>
              <p className="muted">{item.label}</p>
              <strong className="stat-value">{stats[item.key] ?? 0}</strong>
              <p className="metric-caption">{item.hint}</p>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
