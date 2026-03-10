from sqlalchemy import Column, Integer, String

from backend.database import Base


class BotSetting(Base):
    __tablename__ = "bot_settings"

    id = Column(Integer, primary_key=True)
    start_message = Column(
        String,
        nullable=False,
        default="Welcome! Choose a menu option.",
    )
    abandoned_reminder_message = Column(
        String,
        nullable=False,
        default="Вы смотрели товары, но не оставили заявку. Ответьте на это сообщение, и мы поможем оформить заказ.",
    )
    abandoned_reminder_delay_minutes = Column(Integer, nullable=False, default=30)
    consultation_phone = Column(String, nullable=False, default="+7 (000) 000-00-00")
    consultation_message = Column(
        String,
        nullable=False,
        default="📞 Для консультации позвоните по номеру: {phone}\n\n✍️ Или задайте вопрос в сообщении ниже.",
    )
    consultation_contact_prompt = Column(
        String,
        nullable=False,
        default="Спасибо, вопрос получил. Теперь нажмите кнопку ниже и поделитесь номером телефона:",
    )
    about_message = Column(
        String,
        nullable=False,
        default="О компании: мы помогаем подобрать решение под ваш запрос.",
    )
