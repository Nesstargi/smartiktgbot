from aiogram import F, Router
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from bot.api_client import get_bot_settings
from bot.handlers.catalog_common import schedule_bot_subscriber_sync

router = Router()

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛒 Каталог")],
        [
            KeyboardButton(text="🔥 Акции"),
            KeyboardButton(text="❓ Консультация"),
        ],
        [KeyboardButton(text="ℹ️ О компании")],
    ],
    resize_keyboard=True,
)


@router.message(F.text == "/start")
async def start(msg: Message):
    if msg.from_user:
        schedule_bot_subscriber_sync(chat=msg.chat, user=msg.from_user)

    text = "Добро пожаловать! Выберите пункт меню 👇"
    try:
        settings = await get_bot_settings(force_refresh=True)
        if isinstance(settings, dict) and settings.get("start_message"):
            text = settings["start_message"]
    except Exception:
        pass

    await msg.answer(text, reply_markup=menu)
