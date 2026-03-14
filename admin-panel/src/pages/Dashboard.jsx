import { useEffect, useMemo, useState } from "react";

import { getApiErrorMessage } from "../api/axios";
import { getStats } from "../api/dashboard.api";

const primaryItems = [
  { key: "categories", label: "Категории", hint: "Верхний уровень каталога" },
  { key: "subcategories", label: "Подкатегории", hint: "Разделы внутри категорий" },
  { key: "products", label: "Товары", hint: "Позиции, доступные в каталоге" },
  { key: "promotions", label: "Акции", hint: "Маркетинговые предложения" },
  { key: "leads", label: "Заявки", hint: "Контакты и запросы клиентов" },
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

function buildInsights(stats) {
  const insights = [];

  if (stats.products === 0) {
    insights.push("В каталоге пока нет товаров. Пользователю будет нечего показывать в карточках.");
  } else {
    insights.push(`Каталог уже наполнен: ${stats.products} товаров доступны для работы бота и админки.`);
  }

  if (stats.leads === 0) {
    insights.push("Заявок пока нет. Можно проверить сценарии бота и форму захвата лидов.");
  } else {
    insights.push(`В базе ${stats.leads} заявок. Есть с чем работать менеджеру и аналитике.`);
  }

  if (stats.promotions === 0) {
    insights.push("Акций пока нет. Рассылки и промо-блок можно усилить первой кампанией.");
  } else {
    insights.push(`Акционные сценарии уже используются: заведено ${stats.promotions} акций.`);
  }

  return insights;
}

export default function Dashboard() {
  const [stats, setStats] = useState({
    categories: 0,
    subcategories: 0,
    products: 0,
    promotions: 0,
    leads: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);

  const catalogTotal = useMemo(
    () => stats.categories + stats.subcategories + stats.products,
    [stats.categories, stats.products, stats.subcategories],
  );
  const marketingTotal = useMemo(
    () => stats.promotions + stats.leads,
    [stats.leads, stats.promotions],
  );
  const insights = useMemo(() => buildInsights(stats), [stats]);

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
        <>
          <div className="stats-grid">
            {primaryItems.map((item) => (
              <article className="card metric-card" key={item.key}>
                <p className="muted">{item.label}</p>
                <strong className="stat-value">{stats[item.key] ?? 0}</strong>
                <p className="metric-caption">{item.hint}</p>
              </article>
            ))}
          </div>

          <div className="stats-summary-grid">
            <article className="card">
              <h3>Сводка каталога</h3>
              <p className="stat-value">{catalogTotal}</p>
              <p className="muted">Категории, подкатегории и товары вместе.</p>
            </article>
            <article className="card">
              <h3>Рабочая нагрузка</h3>
              <p className="stat-value">{marketingTotal}</p>
              <p className="muted">Суммарно акции и заявки, с которыми работает команда.</p>
            </article>
          </div>

          <div className="insights-grid">
            {insights.map((insight) => (
              <article className="card insight-card" key={insight}>
                <p>{insight}</p>
              </article>
            ))}
          </div>
        </>
      )}
    </section>
  );
}
