import { useMemo, useState } from "react";

import { getApiErrorMessage } from "../api/axios";
import { broadcastNotification } from "../api/notifications.api";
import UploadField from "../components/UploadField";
import { buildMediaUrl } from "../utils/media";

const TITLE_LIMIT = 128;
const MESSAGE_LIMIT = 4096;

export default function NotificationsPage() {
  const [form, setForm] = useState({
    title: "",
    message: "",
    image_url: "",
  });
  const [sending, setSending] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const titleLength = form.title.trim().length;
  const messageLength = form.message.trim().length;
  const canSubmit = useMemo(
    () =>
      titleLength > 0
      && titleLength <= TITLE_LIMIT
      && messageLength > 0
      && messageLength <= MESSAGE_LIMIT,
    [messageLength, titleLength],
  );

  const resultMessage = useMemo(() => {
    if (!result) return "";
    if (result.total === 0) return "Рассылка завершена, но подходящих получателей не нашлось.";
    if (result.failed === 0) return "Рассылка завершена без ошибок.";
    if (result.success === 0) return "Отправка завершилась с ошибками для всех получателей.";
    return "Рассылка завершена частично: часть сообщений ушла успешно, часть нет.";
  }, [result]);

  const onSend = async (e) => {
    e.preventDefault();
    if (!canSubmit) return;

    setSending(true);
    setError("");
    setResult(null);
    try {
      const data = await broadcastNotification({
        title: form.title.trim(),
        message: form.message.trim(),
        image_url: form.image_url.trim() || null,
      });
      setResult(data);
      setForm({
        title: "",
        message: "",
        image_url: "",
      });
    } catch (sendError) {
      setError(getApiErrorMessage(sendError, "Не удалось отправить уведомление"));
    } finally {
      setSending(false);
    }
  };

  const onReset = () => {
    setForm({
      title: "",
      message: "",
      image_url: "",
    });
    setError("");
    setResult(null);
  };

  return (
    <section>
      <div className="stats-header">
        <div>
          <h2 className="page-title">Уведомления</h2>
          <p className="muted">
            Рассылка уйдёт по уникальным `telegram_id`, которые уже попали в заявки.
          </p>
        </div>
        <div className="inline-actions">
          <button type="button" onClick={onReset} disabled={sending}>
            Очистить форму
          </button>
        </div>
      </div>

      <article className="card settings-card">
        <form className="stack-form" onSubmit={onSend}>
          <input
            placeholder="Заголовок"
            value={form.title}
            maxLength={TITLE_LIMIT}
            onChange={(e) => setForm((prev) => ({ ...prev, title: e.target.value }))}
          />
          <div className="counter-row">
            <span className="muted">Короткий заголовок для уведомления</span>
            <span className="muted">{titleLength}/{TITLE_LIMIT}</span>
          </div>

          <textarea
            rows={5}
            placeholder="Текст уведомления"
            value={form.message}
            maxLength={MESSAGE_LIMIT}
            onChange={(e) => setForm((prev) => ({ ...prev, message: e.target.value }))}
          />
          <div className="counter-row">
            <span className="muted">Основное сообщение рассылки</span>
            <span className="muted">{messageLength}/{MESSAGE_LIMIT}</span>
          </div>

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
              decoding="async"
              width={200}
              style={{ width: 200, border: "1px solid #111" }}
            />
          )}

          <article className="card preview-card">
            <h3>Предпросмотр</h3>
            <p><strong>{form.title.trim() || "Без заголовка"}</strong></p>
            <p>{form.message.trim() || "Сообщение появится здесь после ввода текста."}</p>
            <p className="muted">
              {form.image_url ? "Изображение будет приложено к уведомлению." : "Изображение не выбрано."}
            </p>
          </article>

          <div className="inline-actions">
            <button type="submit" disabled={sending || !canSubmit}>
              {sending ? "Отправляем..." : "Отправить уведомление"}
            </button>
            <span className="muted">
              {canSubmit ? "Форма готова к отправке" : "Заполните заголовок и текст"}
            </span>
          </div>
        </form>

        {error && <p className="error-text">{error}</p>}

        {result && (
          <article className="card result-card">
            <h3>Результат рассылки</h3>
            <div className="result-grid">
              <div>
                <p className="muted">Всего получателей</p>
                <strong className="stat-value">{result.total}</strong>
              </div>
              <div>
                <p className="muted">Успешно</p>
                <strong className="stat-value">{result.success}</strong>
              </div>
              <div>
                <p className="muted">Ошибок</p>
                <strong className="stat-value">{result.failed}</strong>
              </div>
            </div>
            <p className="muted">{resultMessage}</p>
          </article>
        )}
      </article>
    </section>
  );
}
