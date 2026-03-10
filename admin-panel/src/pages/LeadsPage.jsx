import { useEffect, useState } from "react";

import { deleteLead, getLeads } from "../api/leads.api";

function formatDateTime(value) {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString("ru-RU", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export default function LeadsPage() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const data = await getLeads();
      setItems(data || []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const onDelete = async (item) => {
    if (!window.confirm(`Удалить заявку #${item.id}?`)) return;
    await deleteLead(item.id);
    await load();
  };

  return (
    <section>
      <h2 className="page-title">Заявки</h2>

      <article className="card">
        {loading ? (
          <p className="muted">Загрузка...</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Дата и время</th>
                <th>Имя</th>
                <th>Телефон</th>
                <th>Telegram ID</th>
                <th>Заявка</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id}>
                  <td>{item.id}</td>
                  <td>{formatDateTime(item.created_at)}</td>
                  <td>{item.name || "-"}</td>
                  <td>{item.phone || "-"}</td>
                  <td>{item.telegram_id || "-"}</td>
                  <td>{item.product || "-"}</td>
                  <td className="actions">
                    <button onClick={() => onDelete(item)}>Удалить</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </article>
    </section>
  );
}
