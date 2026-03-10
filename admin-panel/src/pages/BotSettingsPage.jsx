import { useEffect, useState } from "react";

import { getBotSettings, updateBotSettings } from "../api/botSettings.api";

const DEFAULT_REMINDER =
  "Вы смотрели товары, но не оставили заявку. Ответьте на это сообщение, и мы поможем оформить заказ.";
const DEFAULT_CONSULTATION_PHONE = "+7 (000) 000-00-00";
const DEFAULT_CONSULTATION_MESSAGE =
  "📞 Для консультации позвоните по номеру: {phone}\n\n✍️ Или задайте вопрос в сообщении ниже.";
const DEFAULT_CONSULTATION_CONTACT_PROMPT =
  "Спасибо, вопрос получил. Теперь нажмите кнопку ниже и поделитесь номером телефона:";
const DEFAULT_ABOUT_MESSAGE = "О компании: мы помогаем подобрать решение под ваш запрос.";

export default function BotSettingsPage() {
  const [startMessage, setStartMessage] = useState("");
  const [reminderMessage, setReminderMessage] = useState("");
  const [reminderDelayMinutes, setReminderDelayMinutes] = useState(30);
  const [consultationPhone, setConsultationPhone] = useState("");
  const [consultationMessage, setConsultationMessage] = useState("");
  const [consultationContactPrompt, setConsultationContactPrompt] = useState("");
  const [aboutMessage, setAboutMessage] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const load = async () => {
      const data = await getBotSettings();
      setStartMessage(data.start_message || "");
      setReminderMessage(data.abandoned_reminder_message || DEFAULT_REMINDER);
      setReminderDelayMinutes(Number(data.abandoned_reminder_delay_minutes || 30));
      setConsultationPhone(data.consultation_phone || DEFAULT_CONSULTATION_PHONE);
      setConsultationMessage(data.consultation_message || DEFAULT_CONSULTATION_MESSAGE);
      setConsultationContactPrompt(
        data.consultation_contact_prompt || DEFAULT_CONSULTATION_CONTACT_PROMPT,
      );
      setAboutMessage(data.about_message || DEFAULT_ABOUT_MESSAGE);
    };

    load();
  }, []);

  const onSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await updateBotSettings({
        start_message: startMessage,
        abandoned_reminder_message: reminderMessage,
        abandoned_reminder_delay_minutes: Number(reminderDelayMinutes || 30),
        consultation_phone: consultationPhone,
        consultation_message: consultationMessage,
        consultation_contact_prompt: consultationContactPrompt,
        about_message: aboutMessage,
      });
      window.alert("Настройки сохранены");
    } finally {
      setSaving(false);
    }
  };

  return (
    <section>
      <h2 className="page-title">Настройки бота</h2>
      <form className="settings-layout" onSubmit={onSave}>
        <article className="card settings-section">
          <h3>1. Главное меню</h3>
          <p className="muted">Тексты, которые пользователь видит сразу после старта.</p>
          <label>
            Стартовое сообщение
            <textarea
              rows={5}
              value={startMessage}
              onChange={(e) => setStartMessage(e.target.value)}
            />
          </label>
        </article>

        <article className="card settings-section">
          <h3>2. Напоминания</h3>
          <p className="muted">Автоматическое сообщение, если клиент не завершил заявку.</p>
          <label>
            Сообщение при незавершенной заявке
            <textarea
              rows={5}
              value={reminderMessage}
              onChange={(e) => setReminderMessage(e.target.value)}
            />
          </label>
          <label>
            Через сколько минут отправлять напоминание
            <input
              type="number"
              min={1}
              max={10080}
              value={reminderDelayMinutes}
              onChange={(e) => setReminderDelayMinutes(Number(e.target.value || 1))}
            />
          </label>
        </article>

        <article className="card settings-section">
          <h3>3. Консультация</h3>
          <p className="muted">Сценарий кнопки «Консультация» и текст запроса контакта.</p>
          <label>
            Телефон для консультации
            <input
              value={consultationPhone}
              onChange={(e) => setConsultationPhone(e.target.value)}
              placeholder="+7 (900) 000-00-00"
            />
          </label>
          <label>
            Сообщение при нажатии «Консультация»
            <textarea
              rows={4}
              value={consultationMessage}
              onChange={(e) => setConsultationMessage(e.target.value)}
            />
            <small className="muted">Можно использовать {'{phone}'} для подстановки телефона.</small>
          </label>
          <label>
            Сообщение после вопроса (перед запросом контакта)
            <textarea
              rows={3}
              value={consultationContactPrompt}
              onChange={(e) => setConsultationContactPrompt(e.target.value)}
            />
          </label>
        </article>

        <article className="card settings-section">
          <h3>4. О компании</h3>
          <p className="muted">Текст, который показывается по кнопке «О компании».</p>
          <label>
            Текст страницы «О компании»
            <textarea
              rows={5}
              value={aboutMessage}
              onChange={(e) => setAboutMessage(e.target.value)}
            />
          </label>
        </article>

        <article className="card settings-actions">
          <button type="submit" disabled={saving}>
            {saving ? "Сохранение..." : "Сохранить все настройки"}
          </button>
        </article>
      </form>
    </section>
  );
}
