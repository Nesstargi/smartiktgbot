from aiogram import F, Router
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from bot.api_client import get_bot_settings

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
    text = "Добро пожаловать! Выберите пункт меню 👇"
    try:
        settings = await get_bot_settings()
        if isinstance(settings, dict) and settings.get("start_message"):
            text = settings["start_message"]
    except Exception:
        pass

    await msg.answer(text, reply_markup=menu)
