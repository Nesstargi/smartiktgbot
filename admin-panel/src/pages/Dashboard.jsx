import { useEffect, useState } from "react";

import { getStats } from "../api/dashboard.api";

const items = [
  { key: "categories", label: "Категории" },
  { key: "subcategories", label: "Подкатегории" },
  { key: "products", label: "Товары" },
  { key: "promotions", label: "Акции" },
  { key: "leads", label: "Заявки" },
];

export default function Dashboard() {
  const [stats, setStats] = useState({});

  useEffect(() => {
    const load = async () => {
      const data = await getStats();
      setStats(data);
    };

    load();
  }, []);

  return (
    <section>
      <h2 className="page-title">Дашборд</h2>
      <div className="stats-grid">
        {items.map((item) => (
          <article className="card" key={item.key}>
            <p className="muted">{item.label}</p>
            <strong className="stat-value">{stats[item.key] ?? 0}</strong>
          </article>
        ))}
      </div>
    </section>
  );
}
