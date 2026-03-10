import { useState } from "react";

import { broadcastNotification } from "../api/notifications.api";
import UploadField from "../components/UploadField";
import { buildMediaUrl } from "../utils/media";

export default function NotificationsPage() {
  const [form, setForm] = useState({
    title: "",
    message: "",
    image_url: "",
  });
  const [sending, setSending] = useState(false);
  const [result, setResult] = useState(null);

  const onSend = async (e) => {
    e.preventDefault();
    if (!form.title.trim() || !form.message.trim()) return;

    setSending(true);
    setResult(null);
    try {
      const data = await broadcastNotification({
        title: form.title.trim(),
        message: form.message.trim(),
        image_url: form.image_url.trim() || null,
      });
      setResult(data);
    } finally {
      setSending(false);
    }
  };

  return (
    <section>
      <h2 className="page-title">Уведомления</h2>
      <article className="card settings-card">
        <form className="stack-form" onSubmit={onSend}>
          <input
            placeholder="Заголовок"
            value={form.title}
            onChange={(e) => setForm((prev) => ({ ...prev, title: e.target.value }))}
          />
          <textarea
            rows={5}
            placeholder="Текст уведомления"
            value={form.message}
            onChange={(e) => setForm((prev) => ({ ...prev, message: e.target.value }))}
          />
          <input
            placeholder="URL изображения (опционально)"
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
              style={{ width: 200, border: "1px solid #111" }}
            />
          )}

          <button type="submit" disabled={sending}>
            {sending ? "Отправляем..." : "Отправить уведомление"}
          </button>
        </form>

        {result && (
          <p className="muted">
            Отправка завершена: всего {result.total}, успешно {result.success}, ошибок {result.failed}
          </p>
        )}
      </article>
    </section>
  );
}
