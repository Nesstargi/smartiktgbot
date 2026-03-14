from aiogram import F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot.handlers.menu import menu

from .catalog_common import (
    categories_cache,
    clear_consultation_waiting,
    crumb,
    get_categories_cached,
    get_products_cached,
    lead_contact_keyboard,
    router,
    schedule_catalog_warmup,
    send_product_card,
    send_products_menu,
    send_subcategories_menu,
    subcategories_cache,
    touch_catalog_activity,
)


@router.message(F.text == "🛒 Каталог")
async def show_categories(message: Message):
    if message.from_user:
        await clear_consultation_waiting(message.from_user.id)
        await touch_catalog_activity(message.from_user.id, message.bot, message.chat.id)

    categories = await get_categories_cached()
    schedule_catalog_warmup()

    kb = [[InlineKeyboardButton(text=cat["name"], callback_data=f"cat_{cat['id']}")] for cat in categories]
    kb.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")])
    await message.answer("📦 Выберите категорию:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))


@router.callback_query(F.data.startswith("cat_"))
async def show_subcategories(callback: CallbackQuery):
    await callback.answer()
    cat_id = int(callback.data.split("_")[1])
    await touch_catalog_activity(callback.from_user.id, callback.bot, callback.message.chat.id)
    await send_subcategories_menu(callback, cat_id)


@router.callback_query(F.data.startswith("sub_"))
async def show_products(callback: CallbackQuery):
    await callback.answer()
    sub_id = int(callback.data.split("_")[1])
    await touch_catalog_activity(callback.from_user.id, callback.bot, callback.message.chat.id, sub_id=sub_id)
    await send_products_menu(callback, sub_id)


@router.callback_query(F.data.startswith("prod_"))
async def show_product_card(callback: CallbackQuery):
    await callback.answer()
    _, sub_id, product_id = callback.data.split("_")
    await touch_catalog_activity(
        callback.from_user.id,
        callback.bot,
        callback.message.chat.id,
        sub_id=int(sub_id),
        product_id=int(product_id),
    )
    await send_product_card(callback, int(sub_id), int(product_id))


@router.callback_query(F.data.startswith("lead_"))
async def lead_start(callback: CallbackQuery):
    await callback.answer()
    _, sub_id, product_id = callback.data.split("_")
    sub_id_i = int(sub_id)
    product_id_i = int(product_id)

    sub = subcategories_cache.get(sub_id_i, {})
    sub_name = sub.get("name", "Подкатегория")
    cat_id = sub.get("category_id")
    category_name = categories_cache.get(cat_id, f"Категория {cat_id}") if cat_id else "Каталог"

    products = await get_products_cached(sub_id_i)
    prod = next((p for p in products if p["id"] == product_id_i), None)
    product_name = prod.get("name") if prod else f"Товар {product_id_i}"

    user_id = callback.from_user.id
    await clear_consultation_waiting(user_id)
    await touch_catalog_activity(
        user_id,
        callback.bot,
        callback.message.chat.id,
        sub_id=sub_id_i,
        product_id=product_id_i,
        product_name=product_name,
    )

    await callback.message.answer(
        f"📍 *{crumb('Каталог', category_name, sub_name, product_name)}*\n\n"
        "📞 Нажмите кнопку ниже, чтобы поделиться номером телефона:",
        parse_mode="Markdown",
        reply_markup=lead_contact_keyboard(),
    )


@router.callback_query(F.data.startswith("back_subs_"))
async def back_to_subs(callback: CallbackQuery):
    await callback.answer()
    cat_id = int(callback.data.split("_")[2])
    await touch_catalog_activity(callback.from_user.id, callback.bot, callback.message.chat.id)
    await send_subcategories_menu(callback, cat_id)


@router.callback_query(F.data == "main_menu")
async def back_to_main(callback: CallbackQuery):
    await callback.answer()
    await touch_catalog_activity(callback.from_user.id, callback.bot, callback.message.chat.id)
    await clear_consultation_waiting(callback.from_user.id)
    await callback.message.answer("🏠 Главное меню\n\nВыберите пункт меню 👇", reply_markup=menu)


@router.callback_query(F.data == "back_categories")
async def back_categories(callback: CallbackQuery):
    await callback.answer()
    await touch_catalog_activity(callback.from_user.id, callback.bot, callback.message.chat.id)
    await show_categories(callback.message)


@router.message(F.photo)
async def get_file_id(message: Message):
    file_id = message.photo[-1].file_id
    await message.answer(f"FILE_ID:\n{file_id}")
