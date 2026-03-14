import { useEffect, useMemo, useState } from "react";

import { getApiErrorMessage } from "../api/axios";
import {
  createPromotion,
  deletePromotion,
  getPromotions,
  updatePromotion,
} from "../api/promotions.api";
import UploadField from "../components/UploadField";
import { buildMediaUrl } from "../utils/media";

const PAGE_SIZE = 10;

export default function PromotionsPage() {
  const [items, setItems] = useState([]);
  const [totalItems, setTotalItems] = useState(0);
  const [loading, setLoading] = useState(true);
  const [listError, setListError] = useState("");
  const [formError, setFormError] = useState("");
  const [searchInput, setSearchInput] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [page, setPage] = useState(0);
  const [reloadToken, setReloadToken] = useState(0);
  const [form, setForm] = useState({
    title: "",
    description: "",
    image_url: "",
    is_active: true,
    send_to_all: false,
  });

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

    async function loadPromotions() {
      setLoading(true);
      setListError("");
      try {
        const result = await getPromotions({
          q: searchQuery || undefined,
          is_active:
            statusFilter === "all"
              ? undefined
              : statusFilter === "active",
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
          setListError(getApiErrorMessage(error, "Не удалось загрузить акции"));
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadPromotions();
    return () => {
      cancelled = true;
    };
  }, [page, reloadToken, searchQuery, statusFilter]);

  const refreshPromotions = () => {
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
    setStatusFilter("all");
    setPage(0);
  };

  const onCreate = async (e) => {
    e.preventDefault();
    if (!form.title.trim()) {
      setFormError("Введите название акции");
      return;
    }

    setFormError("");
    try {
      await createPromotion({
        title: form.title.trim(),
        description: form.description.trim() || null,
        image_url: form.image_url.trim() || null,
        is_active: form.is_active,
        send_to_all: form.send_to_all,
      });

      setForm({
        title: "",
        description: "",
        image_url: "",
        is_active: true,
        send_to_all: false,
      });
      refreshPromotions();
    } catch (error) {
      setFormError(getApiErrorMessage(error, "Не удалось создать акцию"));
    }
  };

  const onEdit = async (item) => {
    const title = window.prompt("Название", item.title) ?? item.title;
    const description =
      window.prompt("Описание", item.description ?? "") ?? item.description;

    setListError("");
    try {
      await updatePromotion(item.id, { title, description });
      refreshPromotions();
    } catch (error) {
      setListError(getApiErrorMessage(error, "Не удалось обновить акцию"));
    }
  };

  const onUploadImage = async (item, image_url) => {
    setListError("");
    try {
      await updatePromotion(item.id, { image_url: image_url || null });
      refreshPromotions();
    } catch (error) {
      setListError(getApiErrorMessage(error, "Не удалось обновить изображение"));
    }
  };

  const onToggle = async (item) => {
    setListError("");
    try {
      await updatePromotion(item.id, { is_active: !item.is_active });
      refreshPromotions();
    } catch (error) {
      setListError(getApiErrorMessage(error, "Не удалось обновить статус акции"));
    }
  };

  const onDelete = async (item) => {
    if (!window.confirm(`Удалить акцию "${item.title}"?`)) return;

    setListError("");
    try {
      await deletePromotion(item.id);
      if (items.length === 1 && page > 0) {
        setPage((prev) => prev - 1);
        return;
      }
      refreshPromotions();
    } catch (error) {
      setListError(getApiErrorMessage(error, "Не удалось удалить акцию"));
    }
  };

  return (
    <section>
      <h2 className="page-title">Акции</h2>

      <article className="card">
        <form className="stack-form" onSubmit={onCreate}>
          <input
            placeholder="Название акции"
            value={form.title}
            onChange={(e) => setForm((prev) => ({ ...prev, title: e.target.value }))}
          />
          <textarea
            rows={3}
            placeholder="Описание"
            value={form.description}
            onChange={(e) =>
              setForm((prev) => ({ ...prev, description: e.target.value }))
            }
          />
          <input
            placeholder="URL фото (или загрузите ниже)"
            value={form.image_url}
            onChange={(e) => setForm((prev) => ({ ...prev, image_url: e.target.value }))}
          />
          <UploadField
            onUploaded={(url) => setForm((prev) => ({ ...prev, image_url: url || "" }))}
          />
          {form.image_url && (
            <img
              src={buildMediaUrl(form.image_url)}
              alt="Предпросмотр"
              decoding="async"
              width={180}
              style={{ width: 180, border: "1px solid #111" }}
            />
          )}
          <label className="checkbox">
            <input
              type="checkbox"
              checked={form.is_active}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, is_active: e.target.checked }))
              }
            />
            Активна
          </label>
          <label className="checkbox">
            <input
              type="checkbox"
              checked={form.send_to_all}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, send_to_all: e.target.checked }))
              }
            />
            Отправить всем пользователям
          </label>
          <button type="submit">Добавить акцию</button>
          {formError && <p className="error-text">{formError}</p>}
        </form>
      </article>

      <article className="card">
        <div className="list-toolbar">
          <form className="inline-form" onSubmit={onSearchSubmit}>
            <input
              placeholder="Поиск по названию или описанию"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
            />
            <button type="submit">Найти</button>
            <button
              type="button"
              onClick={onClearSearch}
              disabled={!searchInput && !searchQuery && statusFilter === "all"}
            >
              Сбросить
            </button>
          </form>

          <div className="inline-form">
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setPage(0);
              }}
            >
              <option value="all">Все статусы</option>
              <option value="active">Только активные</option>
              <option value="inactive">Только скрытые</option>
            </select>
          </div>
        </div>

        <p className="muted">{loading ? "Загрузка..." : resultsLabel}</p>
        {listError && <p className="error-text">{listError}</p>}

        {loading ? (
          <p className="muted">Загрузка...</p>
        ) : items.length === 0 ? (
          <p className="muted">Акции не найдены.</p>
        ) : (
          <div className="table-wrap">
            <table className="table table-compact">
              <thead>
                <tr>
                  <th>Фото</th>
                  <th>Название</th>
                  <th>Описание</th>
                  <th>Статус</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.id}>
                    <td data-label="Фото">
                      {item.image_url ? (
                        <img
                          src={buildMediaUrl(item.image_url)}
                          alt={item.title}
                          loading="lazy"
                          decoding="async"
                          width={90}
                          height={60}
                          style={{
                            width: 90,
                            height: 60,
                            objectFit: "cover",
                            border: "1px solid #111",
                          }}
                        />
                      ) : (
                        "-"
                      )}
                    </td>
                    <td data-label="Название">{item.title}</td>
                    <td data-label="Описание">{item.description || "-"}</td>
                    <td data-label="Статус">{item.is_active ? "Активна" : "Скрыта"}</td>
                    <td className="actions" data-label="Действия">
                      <button onClick={() => onEdit(item)}>Изменить</button>
                      <UploadField
                        compact
                        label="Загрузить фото"
                        onUploaded={(url) => onUploadImage(item, url)}
                      />
                      <button onClick={() => onToggle(item)}>
                        {item.is_active ? "Скрыть" : "Показать"}
                      </button>
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
