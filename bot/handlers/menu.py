from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

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
    await msg.answer("Добро пожаловать! Выберите пункт меню 👇", reply_markup=menu)
