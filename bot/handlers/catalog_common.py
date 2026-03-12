import asyncio
from pathlib import Path
from urllib.parse import urlparse

from aiogram import Router
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)

from bot.api_client import API_URL, fetch_bytes, get_bot_settings, get_products, get_subcategories

router = Router()

lead_requests: dict[int, dict] = {}
reminder_tasks: dict[int, asyncio.Task] = {}
reminder_reply_waiting: dict[int, dict] = {}
consultation_waiting_question: dict[int, bool] = {}
subcategories_cache: dict[int, dict] = {}
categories_cache: dict[int, str] = {}
media_file_id_cache: dict[str, str] = {}

DEFAULT_ABANDONED_REMINDER_MESSAGE = (
    "Вы смотрели товары, но не оставили заявку. "
    "Ответьте на это сообщение, и мы поможем оформить заказ."
)
DEFAULT_ABANDONED_REMINDER_DELAY_MINUTES = 30
DEFAULT_CONSULTATION_PHONE = "+7 (000) 000-00-00"
DEFAULT_CONSULTATION_MESSAGE = (
    "📞 Для консультации позвоните по номеру: {phone}\n\n"
    "✍️ Или задайте вопрос в сообщении ниже."
)
DEFAULT_CONSULTATION_CONTACT_PROMPT = (
    "Спасибо, вопрос получил. Теперь нажмите кнопку ниже и поделитесь номером телефона:"
)
DEFAULT_ABOUT_MESSAGE = "О компании: мы помогаем подобрать решение под ваш запрос."


def product_text(product: dict) -> str:
    return f"📦 *{product['name']}*\n\n📝 {product.get('description') or 'Описание отсутствует'}"


def crumb(*parts: str) -> str:
    safe_parts = [p for p in parts if p]
    return " > ".join(safe_parts)


def full_media_url(path_or_url: str | None):
    if not path_or_url:
        return None
    if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        return path_or_url
    if path_or_url.startswith("/"):
        return f"{API_URL}{path_or_url}"

    # Поддержка старых записей, где в БД хранится только имя файла.
    if "/" not in path_or_url:
        return f"{API_URL}/media/{path_or_url}"

    return f"{API_URL}/{path_or_url.lstrip('/')}"


def is_local_url(url: str) -> bool:
    parsed_url = urlparse(url)
    parsed_api = urlparse(API_URL)

    hostname = (parsed_url.hostname or "").lower()
    api_hostname = (parsed_api.hostname or "").lower()

    if hostname in {"127.0.0.1", "localhost", "0.0.0.0", "backend"}:
        return True

    if api_hostname and hostname == api_hostname:
        return True

    return False


def media_cache_key(photo_ref: str | None) -> str | None:
    value = full_media_url(photo_ref)
    if not value:
        return None
    return value


def remember_sent_photo(photo_ref: str | None, sent_message: Message):
    key = media_cache_key(photo_ref)
    if not key:
        return

    photo_sizes = getattr(sent_message, "photo", None)
    if not photo_sizes:
        return

    media_file_id_cache[key] = photo_sizes[-1].file_id


def cancel_reminder_task(user_id: int):
    task = reminder_tasks.pop(user_id, None)
    if task and not task.done():
        task.cancel()


def touch_catalog_activity(
    user_id: int,
    bot,
    chat_id: int,
    *,
    sub_id: int | None = None,
    product_id: int | None = None,
    product_name: str | None = None,
):
    context = lead_requests.get(user_id, {}).copy()
    context["bot"] = bot
    context["chat_id"] = chat_id

    if sub_id is not None:
        context["sub_id"] = sub_id
    if product_id is not None:
        context["product_id"] = product_id
    if product_name is not None:
        context["product_name"] = product_name

    lead_requests[user_id] = context
    reminder_reply_waiting.pop(user_id, None)
    cancel_reminder_task(user_id)
    reminder_tasks[user_id] = asyncio.create_task(schedule_abandoned_reminder(user_id, chat_id))


async def schedule_abandoned_reminder(user_id: int, chat_id: int):
    current_task = asyncio.current_task()
    try:
        try:
            settings = await get_bot_settings()
            delay_minutes = int(
                settings.get(
                    "abandoned_reminder_delay_minutes",
                    DEFAULT_ABANDONED_REMINDER_DELAY_MINUTES,
                )
            )
            if delay_minutes < 1:
                delay_minutes = 1
            reminder_text = settings.get("abandoned_reminder_message") or DEFAULT_ABANDONED_REMINDER_MESSAGE
        except Exception:
            delay_minutes = DEFAULT_ABANDONED_REMINDER_DELAY_MINUTES
            reminder_text = DEFAULT_ABANDONED_REMINDER_MESSAGE

        await asyncio.sleep(delay_minutes * 60)

        context = lead_requests.get(user_id)
        if not context:
            return

        sent = await context["bot"].send_message(
            chat_id,
            f"{reminder_text}\n\nОтветьте на это сообщение, и я снова попрошу номер телефона.",
        )
        reminder_reply_waiting[user_id] = {
            **context,
            "prompt_message_id": sent.message_id,
        }
    finally:
        if reminder_tasks.get(user_id) is current_task:
            reminder_tasks.pop(user_id, None)


async def photo_payload(photo_ref: str | None):
    if not photo_ref:
        return None

    value = full_media_url(photo_ref)
    if not value:
        return None

    cached_file_id = media_file_id_cache.get(value)
    if cached_file_id:
        return cached_file_id

    if value.startswith("http://") or value.startswith("https://"):
        if not is_local_url(value):
            return value

        filename = Path(value.split("?", 1)[0]).name or "image.jpg"
        content = await fetch_bytes(value, cache_seconds=90)
        if not content:
            return None
        return BufferedInputFile(content, filename=filename)

    return value


async def send_subcategories_menu(callback: CallbackQuery, cat_id: int):
    subcategories = await get_subcategories(cat_id)
    for s in subcategories:
        subcategories_cache[s["id"]] = s

    category_name = categories_cache.get(cat_id, f"Категория {cat_id}")

    kb = [
        [InlineKeyboardButton(text=sub["name"], callback_data=f"sub_{sub['id']}")]
        for sub in subcategories
    ]
    kb.append([InlineKeyboardButton(text="🔙 К категориям", callback_data="back_categories")])

    await callback.message.answer(
        f"📂 *{crumb('Каталог', category_name)}*\n\nВыберите подкатегорию:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
    )


async def send_products_menu(callback: CallbackQuery, sub_id: int):
    products = await get_products(sub_id)
    if not products:
        await callback.message.answer("❌ В этой подкатегории пока нет товаров")
        return

    sub = subcategories_cache.get(sub_id, {})
    sub_name = sub.get("name", "Подкатегория")
    sub_image = sub.get("image_url")
    cat_id = sub.get("category_id")
    category_name = categories_cache.get(cat_id, f"Категория {cat_id}") if cat_id else "Каталог"

    kb = [
        [InlineKeyboardButton(text=p["name"], callback_data=f"prod_{sub_id}_{p['id']}")]
        for p in products
    ]
    if cat_id:
        kb.append([InlineKeyboardButton(text="🔙 К подкатегориям", callback_data=f"back_subs_{cat_id}")])
    kb.append([InlineKeyboardButton(text="🏠 В меню", callback_data="main_menu")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    caption = f"📂 *{crumb('Каталог', category_name, sub_name)}*\n\nВыберите товар:"
    photo = await photo_payload(sub_image)

    try:
        await callback.message.delete()
    except Exception:
        pass

    if photo:
        try:
            sent = await callback.message.answer_photo(
                photo=photo,
                caption=caption,
                parse_mode="Markdown",
                reply_markup=keyboard,
            )
            remember_sent_photo(sub_image, sent)
            return
        except Exception:
            pass

    await callback.message.answer(caption, parse_mode="Markdown", reply_markup=keyboard)


async def send_product_card(callback: CallbackQuery, sub_id: int, product_id: int):
    products = await get_products(sub_id)
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        await callback.message.answer("Товар не найден")
        return

    sub = subcategories_cache.get(sub_id, {})
    sub_name = sub.get("name", "Подкатегория")
    cat_id = sub.get("category_id")
    category_name = categories_cache.get(cat_id, f"Категория {cat_id}") if cat_id else "Каталог"

    rows = [
        [InlineKeyboardButton(text="📝 Оставить заявку", callback_data=f"lead_{sub_id}_{product_id}")],
        [InlineKeyboardButton(text="🔙 К товарам", callback_data=f"sub_{sub_id}")],
    ]
    if cat_id:
        rows.append([InlineKeyboardButton(text="↩ К подкатегориям", callback_data=f"back_subs_{cat_id}")])
    rows.append([InlineKeyboardButton(text="🏠 В меню", callback_data="main_menu")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=rows)
    photo = await photo_payload(product.get("image_file_id"))
    text = f"📍 *{crumb('Каталог', category_name, sub_name, product['name'])}*\n\n" + product_text(product)

    try:
        await callback.message.delete()
    except Exception:
        pass

    if photo:
        try:
            sent = await callback.message.answer_photo(
                photo=photo,
                caption=text,
                parse_mode="Markdown",
                reply_markup=keyboard,
            )
            remember_sent_photo(product.get("image_file_id"), sent)
            return
        except Exception:
            pass

    await callback.message.answer(text, parse_mode="Markdown", reply_markup=keyboard)


def lead_contact_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📞 Поделиться номером", request_contact=True)],
            [KeyboardButton(text="❌ Отмена")],
            [KeyboardButton(text="🏠 Главное меню")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
