from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from bot.api_client import get_categories, get_subcategories, get_products
import aiohttp

router = Router()
API_URL = "http://127.0.0.1:8000"


# =========================
# КАТАЛОГ → КАТЕГОРИИ
# =========================
@router.message(F.text == "🛒 Каталог")
async def show_categories(message: Message):
    categories = await get_categories()

    kb = [
        [InlineKeyboardButton(text=cat["name"], callback_data=f"cat_{cat['id']}")]
        for cat in categories
    ]

    kb.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    await message.answer("📦 Выберите категорию:", reply_markup=keyboard)


# =========================
# ПОДКАТЕГОРИИ
# =========================
@router.callback_query(F.data.startswith("cat_"))
async def show_subcategories(callback: CallbackQuery):
    cat_id = int(callback.data.split("_")[1])
    subcategories = await get_subcategories(cat_id)

    kb = [
        [InlineKeyboardButton(text=sub["name"], callback_data=f"sub_{sub['id']}")]
        for sub in subcategories
    ]

    kb.append(
        [
            InlineKeyboardButton(
                text="🔙 Назад к категориям", callback_data="back_to_categories"
            )
        ]
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    await callback.message.edit_text("📂 Выберите подкатегорию:", reply_markup=keyboard)


# =========================
# ТОВАРЫ (КАРТОЧКИ)
# =========================
@router.callback_query(F.data.startswith("sub_"))
async def show_products(callback: CallbackQuery):
    sub_id = int(callback.data.split("_")[1])
    products = await get_products(sub_id)

    if not products:
        await callback.message.answer("❌ В этой подкатегории пока нет товаров")
        return

    await callback.message.delete()

    for p in products:
        text = (
            f"📦 *{p['name']}*\n\n📝 {p.get('description') or 'Описание отсутствует'}"
        )

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📝 Оставить заявку", callback_data=f"lead_{p['id']}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🔙 Назад к подкатегориям",
                        callback_data="back_to_subcategories",
                    )
                ],
            ]
        )

        # ✅ Telegram CDN file_id
        if p.get("image_file_id"):
            await callback.message.answer_photo(
                photo=p["image_file_id"],
                caption=text,
                reply_markup=keyboard,
                parse_mode="Markdown",
            )
        else:
            await callback.message.answer(
                text, reply_markup=keyboard, parse_mode="Markdown"
            )


# =========================
# ЗАЯВКА → КОНТАКТ
# =========================
@router.callback_query(F.data.startswith("lead_"))
async def lead_start(callback: CallbackQuery):
    prod_id = int(callback.data.split("_")[1])

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📞 Поделиться номером", request_contact=True)],
            [KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    callback.message.conf = {"product_id": prod_id}

    await callback.message.answer(
        "📞 Нажмите кнопку ниже, чтобы поделиться номером телефона:",
        reply_markup=keyboard,
    )


# =========================
# ПОЛУЧЕНИЕ КОНТАКТА
# =========================
@router.message(F.contact)
async def handle_contact(message: Message):
    phone = message.contact.phone_number
    user_id = message.from_user.id
    name = message.from_user.full_name
    product_id = getattr(message, "conf", {}).get("product_id")

    async with aiohttp.ClientSession() as session:
        await session.post(
            f"{API_URL}/leads",
            json={
                "name": name,
                "phone": phone,
                "telegram_id": user_id,
                "product": product_id,
            },
        )

    await message.answer(
        "✅ Заявка отправлена!\n\nНаш менеджер скоро свяжется с вами 📞"
    )


# =========================
# НАВИГАЦИЯ
# =========================
@router.callback_query(F.data == "main_menu")
async def back_to_main(callback: CallbackQuery):
    await callback.message.answer("🏠 Главное меню\n\nВыберите пункт меню 👇")


@router.callback_query(F.data == "back_to_categories")
async def back_categories(callback: CallbackQuery):
    await show_categories(callback.message)


@router.callback_query(F.data == "back_to_subcategories")
async def back_subcategories(callback: CallbackQuery):
    await callback.message.answer("⬅ Вернитесь к выбору подкатегории через каталог")


# =========================
# DEBUG: получение file_id фото
# =========================
@router.message(F.photo)
async def get_file_id(message: Message):
    file_id = message.photo[-1].file_id  # самое большое разрешение
    await message.answer(f"FILE_ID:\n{file_id}")
