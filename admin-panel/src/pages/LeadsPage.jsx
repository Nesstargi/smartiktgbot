import { useEffect, useMemo, useState } from "react";

import { getApiErrorMessage } from "../api/axios";
import { deleteLead, getLeads } from "../api/leads.api";

const PAGE_SIZE = 15;

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
  const [totalItems, setTotalItems] = useState(0);
  const [loading, setLoading] = useState(true);
  const [listError, setListError] = useState("");
  const [searchInput, setSearchInput] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [page, setPage] = useState(0);
  const [reloadToken, setReloadToken] = useState(0);

  const canGoPrev = page > 0;
  const canGoNext = (page + 1) * PAGE_SIZE < totalItems;
  const resultsLabel = useMemo(() => {
    if (totalItems === 0 || items.length === 0) return "Ничего не найдено";

    const start = page * PAGE_SIZE + 1;
    const end = page * PAGE_SIZE + items.length;
    return `Показано ${start}-${end} из ${totalItems}`;
  }, [items.length, page, totalItems]);

  useEffect(() => {
    let cancelled = false;

    async function loadLeads() {
      setLoading(true);
      setListError("");
      try {
        const result = await getLeads({
          q: searchQuery || undefined,
          limit: PAGE_SIZE,
          offset: page * PAGE_SIZE,
        });

        if (!cancelled) {
          setItems(result.items || []);
          setTotalItems(result.total || 0);
        }
      } catch (error) {
        if (!cancelled) {
          setItems([]);
          setTotalItems(0);
          setListError(getApiErrorMessage(error, "Не удалось загрузить заявки"));
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadLeads();
    return () => {
      cancelled = true;
    };
  }, [page, reloadToken, searchQuery]);

  const refreshLeads = () => {
    setReloadToken((prev) => prev + 1);
  };

  const onSearchSubmit = (e) => {
    e.preventDefault();
    setPage(0);
    setSearchQuery(searchInput.trim());
  };

  const onClearSearch = () => {
    setSearchInput("");
    setSearchQuery("");
    setPage(0);
  };

  const onDelete = async (item) => {
    if (!window.confirm(`Удалить заявку #${item.id}?`)) return;

    setListError("");
    try {
      await deleteLead(item.id);
      if (items.length === 1 && page > 0) {
        setPage((prev) => prev - 1);
        return;
      }
      refreshLeads();
    } catch (error) {
      setListError(getApiErrorMessage(error, "Не удалось удалить заявку"));
    }
  };

  return (
    <section>
      <h2 className="page-title">Заявки</h2>

      <article className="card">
        <div className="list-toolbar">
          <form className="inline-form" onSubmit={onSearchSubmit}>
            <input
              placeholder="Поиск по имени, телефону, telegram или товару"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
            />
            <button type="submit">Найти</button>
            <button
              type="button"
              onClick={onClearSearch}
              disabled={!searchInput && !searchQuery}
            >
              Сбросить
            </button>
          </form>
          <p className="muted">{loading ? "Загрузка..." : resultsLabel}</p>
        </div>

        {listError && <p className="error-text">{listError}</p>}

        {loading ? (
          <p className="muted">Загрузка...</p>
        ) : items.length === 0 ? (
          <p className="muted">Заявки не найдены.</p>
        ) : (
          <div className="table-wrap">
            <table className="table table-compact">
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
                    <td data-label="ID">{item.id}</td>
                    <td data-label="Дата и время">{formatDateTime(item.created_at)}</td>
                    <td data-label="Имя">{item.name || "-"}</td>
                    <td data-label="Телефон">{item.phone || "-"}</td>
                    <td data-label="Telegram ID">{item.telegram_id || "-"}</td>
                    <td data-label="Заявка">{item.product || "-"}</td>
                    <td className="actions" data-label="Действия">
                      <button onClick={() => onDelete(item)}>Удалить</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="pagination-controls">
          <button type="button" onClick={() => setPage((prev) => prev - 1)} disabled={!canGoPrev}>
            Назад
          </button>
          <span className="muted">Страница {page + 1}</span>
          <button type="button" onClick={() => setPage((prev) => prev + 1)} disabled={!canGoNext}>
            Вперёд
          </button>
        </div>
      </article>
    </section>
  );
}
