import { useEffect, useState } from "react";

import {
  createPromotion,
  deletePromotion,
  getPromotions,
  updatePromotion,
} from "../api/promotions.api";
import UploadField from "../components/UploadField";
import { buildMediaUrl } from "../utils/media";

export default function PromotionsPage() {
  const [items, setItems] = useState([]);
  const [form, setForm] = useState({
    title: "",
    description: "",
    image_url: "",
    is_active: true,
    send_to_all: false,
  });

  const load = async () => {
    const data = await getPromotions();
    setItems(data);
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- initial data fetch updates local state
    load();
  }, []);

  const onCreate = async (e) => {
    e.preventDefault();
    if (!form.title.trim()) return;

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
    await load();
  };

  const onEdit = async (item) => {
    const title = window.prompt("Название", item.title) ?? item.title;
    const description =
      window.prompt("Описание", item.description ?? "") ?? item.description;

    await updatePromotion(item.id, { title, description });
    await load();
  };

  const onUploadImage = async (item, image_url) => {
    await updatePromotion(item.id, { image_url: image_url || null });
    await load();
  };

  const onToggle = async (item) => {
    await updatePromotion(item.id, { is_active: !item.is_active });
    await load();
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
        </form>
      </article>

      <article className="card">
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
                      style={{ width: 90, height: 60, objectFit: "cover", border: "1px solid #111" }}
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
                    <button onClick={() => deletePromotion(item.id).then(load)}>
                      Удалить
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </article>
    </section>
  );
}
