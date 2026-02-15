from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from bot.api_client import get_categories, get_subcategories, get_products

router = Router()


# Нажатие на "Каталог"
@router.message(F.text == "🛒 Каталог")
async def show_categories(message: Message):
    categories = await get_categories()

    kb = []
    for cat in categories:
        kb.append(
            [InlineKeyboardButton(text=cat["name"], callback_data=f"cat_{cat['id']}")]
        )

    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    await message.answer("📦 Выберите категорию:", reply_markup=keyboard)


# Подкатегории
@router.callback_query(F.data.startswith("cat_"))
async def show_subcategories(callback: CallbackQuery):
    cat_id = int(callback.data.split("_")[1])
    subcategories = await get_subcategories(cat_id)

    kb = []
    for sub in subcategories:
        kb.append(
            [InlineKeyboardButton(text=sub["name"], callback_data=f"sub_{sub['id']}")]
        )

    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    await callback.message.edit_text("📂 Выберите подкатегорию:", reply_markup=keyboard)


# Товары
@router.callback_query(F.data.startswith("sub_"))
async def show_products(callback: CallbackQuery):
    sub_id = int(callback.data.split("_")[1])
    products = await get_products(sub_id)

    kb = []
    for p in products:
        kb.append(
            [
                InlineKeyboardButton(
                    text=f"{p['name']} — {p['price']} ₽",
                    callback_data=f"prod_{p['id']}",
                )
            ]
        )

    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    await callback.message.edit_text("🛍 Товары:", reply_markup=keyboard)
