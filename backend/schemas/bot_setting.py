from pydantic import BaseModel, Field


DEFAULT_REMINDER = (
    "Вы смотрели товары, но не оставили заявку. "
    "Ответьте на это сообщение, и мы поможем оформить заказ."
)
DEFAULT_CONSULTATION_PHONE = "+7 (000) 000-00-00"
DEFAULT_CONSULTATION_MESSAGE = (
    "📞 Для консультации позвоните по номеру: {phone}\n\n"
    "✍️ Или задайте вопрос в сообщении ниже."
)
DEFAULT_CONSULTATION_CONTACT_PROMPT = (
    "Спасибо, вопрос получил. Теперь нажмите кнопку ниже и поделитесь номером телефона:"
)
DEFAULT_ABOUT_MESSAGE = "О компании: мы помогаем подобрать решение под ваш запрос."


class BotSettingsOut(BaseModel):
    start_message: str
    abandoned_reminder_message: str
    abandoned_reminder_delay_minutes: int
    consultation_phone: str
    consultation_message: str
    consultation_contact_prompt: str
    about_message: str


class BotSettingsUpdate(BaseModel):
    start_message: str
    abandoned_reminder_message: str = Field(default=DEFAULT_REMINDER)
    abandoned_reminder_delay_minutes: int = Field(default=30, ge=1, le=10080)
    consultation_phone: str = Field(default=DEFAULT_CONSULTATION_PHONE, min_length=3, max_length=64)
    consultation_message: str = Field(default=DEFAULT_CONSULTATION_MESSAGE, min_length=5, max_length=2000)
    consultation_contact_prompt: str = Field(
        default=DEFAULT_CONSULTATION_CONTACT_PROMPT,
        min_length=5,
        max_length=500,
    )
    about_message: str = Field(default=DEFAULT_ABOUT_MESSAGE, min_length=5, max_length=4000)
