import asyncio
import ipaddress
import json
import logging
import os
import time
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse

from aiogram import Router
from aiogram.exceptions import TelegramNetworkError, TelegramServerError
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)
from PIL import Image, ImageOps, UnidentifiedImageError

from bot.api_client import (
    API_URL,
    fetch_bytes,
    get_bot_settings,
    get_categories,
    get_products,
    get_subcategories,
)
from bot.runtime_store import runtime_store

router = Router()
logger = logging.getLogger(__name__)

lead_requests: dict[int, dict] = {}
reminder_tasks: dict[int, asyncio.Task] = {}
reminder_reply_waiting: dict[int, dict] = {}
consultation_waiting_question: dict[int, bool] = {}
subcategories_cache: dict[int, dict] = {}
categories_cache: dict[int, str] = {}
category_lists_cache: dict[str, tuple[float, list[dict]]] = {}
subcategory_lists_cache: dict[int, tuple[float, list[dict]]] = {}
products_cache: dict[int, tuple[float, list[dict]]] = {}
catalog_warmup_task: asyncio.Task | None = None
catalog_warmup_lock = asyncio.Lock()
catalog_warmup_expires_at = 0.0

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
CATALOG_CACHE_TTL_SECONDS = 300
PRODUCTS_CACHE_TTL_SECONDS = 90
LEAD_STATE_TTL_SECONDS = int(os.getenv("BOT_STATE_TTL_SECONDS", "86400"))
REMINDER_STATE_TTL_SECONDS = int(os.getenv("BOT_REMINDER_STATE_TTL_SECONDS", "172800"))
MEDIA_FILE_ID_TTL_SECONDS = int(os.getenv("BOT_MEDIA_FILE_ID_TTL_SECONDS", "2592000"))
CATALOG_WARMUP_TTL_SECONDS = int(os.getenv("BOT_CATALOG_WARMUP_TTL_SECONDS", "300"))
MEDIA_ROOT = Path(__file__).resolve().parents[2] / "backend" / "media"
MEDIA_CACHE_PATH = Path(__file__).resolve().parents[1] / "cache" / "media_file_ids.json"
TELEGRAM_IMAGE_MAX_SIZE = 1600
TELEGRAM_JPEG_QUALITY = 85
CALLBACK_ACK_TIMEOUT_SECONDS = float(os.getenv("BOT_CALLBACK_ACK_TIMEOUT_SECONDS", "3").strip() or "3")


def _load_media_file_id_cache() -> dict[str, str]:
    if not MEDIA_CACHE_PATH.exists():
        return {}

    try:
        data = json.loads(MEDIA_CACHE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

    if not isinstance(data, dict):
        return {}

    cache: dict[str, str] = {}
    for key, value in data.items():
        if not key or not value:
            continue
        cache[str(key)] = str(value)
    return cache


def _persist_media_file_id_cache():
    MEDIA_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    temp_path = MEDIA_CACHE_PATH.with_suffix(".tmp")
    temp_path.write_text(
        json.dumps(media_file_id_cache, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )
    temp_path.replace(MEDIA_CACHE_PATH)


media_file_id_cache: dict[str, str] = _load_media_file_id_cache()


def _lead_request_key(user_id: int) -> str:
    return f"bot:state:lead_request:{user_id}"


def _reminder_reply_key(user_id: int) -> str:
    return f"bot:state:reminder_reply:{user_id}"


def _consultation_waiting_key(user_id: int) -> str:
    return f"bot:state:consultation_waiting:{user_id}"


def _reminder_schedule_key(user_id: int) -> str:
    return f"bot:state:reminder_schedule:{user_id}"


def _products_cache_key(sub_id: int) -> str:
    return f"bot:cache:products:{sub_id}"


def _categories_cache_key() -> str:
    return "bot:cache:categories"


def _subcategories_cache_key(cat_id: int) -> str:
    return f"bot:cache:subcategories:{cat_id}"


def _media_file_id_store_key(cache_key: str) -> str:
    return f"bot:cache:media_file_id:{cache_key}"


def _category_lists_cache_get():
    hit = category_lists_cache.get("all")
    if not hit:
        return None
    expires_at, value = hit
    if expires_at < time.monotonic():
        category_lists_cache.pop("all", None)
        return None
    return value


def _category_lists_cache_set(value: list[dict], ttl_seconds: int = CATALOG_CACHE_TTL_SECONDS):
    category_lists_cache["all"] = (time.monotonic() + ttl_seconds, value)


def _subcategory_lists_cache_get(cat_id: int):
    hit = subcategory_lists_cache.get(cat_id)
    if not hit:
        return None
    expires_at, value = hit
    if expires_at < time.monotonic():
        subcategory_lists_cache.pop(cat_id, None)
        return None
    return value


def _subcategory_lists_cache_set(
    cat_id: int,
    value: list[dict],
    ttl_seconds: int = CATALOG_CACHE_TTL_SECONDS,
):
    subcategory_lists_cache[cat_id] = (time.monotonic() + ttl_seconds, value)


def _products_cache_get(sub_id: int):
    hit = products_cache.get(sub_id)
    if not hit:
        return None
    expires_at, value = hit
    if expires_at < time.monotonic():
        products_cache.pop(sub_id, None)
        return None
    return value


def _products_cache_set(sub_id: int, value: list[dict], ttl_seconds: int = PRODUCTS_CACHE_TTL_SECONDS):
    products_cache[sub_id] = (time.monotonic() + ttl_seconds, value)


def _populate_categories_cache(items: list[dict]):
    categories_cache.clear()
    for item in items:
        item_id = item.get("id")
        item_name = item.get("name")
        if item_id is None or not item_name:
            continue
        categories_cache[int(item_id)] = str(item_name)


def _populate_subcategories_cache(items: list[dict]):
    for item in items:
        item_id = item.get("id")
        if item_id is None:
            continue
        subcategories_cache[int(item_id)] = item


async def get_categories_cached(force_refresh: bool = False):
    if not force_refresh:
        cached = _category_lists_cache_get()
        if cached is not None:
            return cached

        cached = await runtime_store.get_json(_categories_cache_key())
        if isinstance(cached, list):
            _category_lists_cache_set(cached)
            _populate_categories_cache(cached)
            return cached

    categories = await get_categories()
    _category_lists_cache_set(categories)
    _populate_categories_cache(categories)
    await runtime_store.set_json(_categories_cache_key(), categories, CATALOG_CACHE_TTL_SECONDS)
    return categories


async def get_subcategories_cached(cat_id: int, force_refresh: bool = False):
    if not force_refresh:
        cached = _subcategory_lists_cache_get(cat_id)
        if cached is not None:
            return cached

        cached = await runtime_store.get_json(_subcategories_cache_key(cat_id))
        if isinstance(cached, list):
            _subcategory_lists_cache_set(cat_id, cached)
            _populate_subcategories_cache(cached)
            return cached

    subcategories = await get_subcategories(cat_id)
    _subcategory_lists_cache_set(cat_id, subcategories)
    _populate_subcategories_cache(subcategories)
    await runtime_store.set_json(
        _subcategories_cache_key(cat_id),
        subcategories,
        CATALOG_CACHE_TTL_SECONDS,
    )
    return subcategories


async def warm_catalog_cache(force_refresh: bool = False):
    global catalog_warmup_expires_at

    async with catalog_warmup_lock:
        if not force_refresh and catalog_warmup_expires_at > time.monotonic():
            return

        try:
            categories = await get_categories_cached(force_refresh=force_refresh)
            if categories:
                results = await asyncio.gather(
                    *(get_subcategories_cached(cat["id"], force_refresh=force_refresh) for cat in categories),
                    return_exceptions=True,
                )
                for result in results:
                    if isinstance(result, Exception):
                        logger.debug("Catalog warmup subcategory fetch failed: %s", result)
            catalog_warmup_expires_at = time.monotonic() + CATALOG_WARMUP_TTL_SECONDS
        except Exception:
            logger.debug("Catalog warmup failed", exc_info=True)


def schedule_catalog_warmup(force_refresh: bool = False):
    global catalog_warmup_task

    if catalog_warmup_task and not catalog_warmup_task.done():
        return catalog_warmup_task

    async def _runner():
        global catalog_warmup_task
        try:
            await warm_catalog_cache(force_refresh=force_refresh)
        finally:
            catalog_warmup_task = None

    catalog_warmup_task = asyncio.create_task(_runner())
    return catalog_warmup_task


async def shutdown_background_tasks():
    global catalog_warmup_task

    tasks: list[asyncio.Task] = []

    warmup_task = catalog_warmup_task
    catalog_warmup_task = None
    if warmup_task is not None and not warmup_task.done():
        warmup_task.cancel()
        tasks.append(warmup_task)

    for user_id, task in list(reminder_tasks.items()):
        reminder_tasks.pop(user_id, None)
        if task is not None and not task.done():
            task.cancel()
            tasks.append(task)

    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)


async def get_products_cached(sub_id: int):
    cached = _products_cache_get(sub_id)
    if cached is not None:
        return cached
    cached = await runtime_store.get_json(_products_cache_key(sub_id))
    if isinstance(cached, list):
        _products_cache_set(sub_id, cached)
        return cached
    products = await get_products(sub_id)
    _products_cache_set(sub_id, products)
    await runtime_store.set_json(_products_cache_key(sub_id), products, PRODUCTS_CACHE_TTL_SECONDS)
    return products


def product_text(product: dict) -> str:
    return f"📦 *{product['name']}*\n\n📝 {product.get('description') or 'Описание отсутствует'}"


def crumb(*parts: str) -> str:
    safe_parts = [p for p in parts if p]
    return " > ".join(safe_parts)


def full_media_url(path_or_url: str | None):
    if not path_or_url:
        return None
    if _looks_like_telegram_file_id(path_or_url):
        return path_or_url
    if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        return path_or_url
    if path_or_url.startswith("/"):
        return f"{API_URL}{path_or_url}"

    # Поддержка старых записей, где в БД хранится только имя файла.
    if "/" not in path_or_url:
        return f"{API_URL}/media/{path_or_url}"

    return f"{API_URL}/{path_or_url.lstrip('/')}"


def _resolve_local_media_path(photo_ref: str | None) -> Path | None:
    if not photo_ref:
        return None

    value = str(photo_ref).strip()
    if not value:
        return None

    if _looks_like_telegram_file_id(value):
        return None

    if value.startswith("http://") or value.startswith("https://"):
        parsed = urlparse(value)
        if parsed.path.startswith("/media/"):
            candidate = MEDIA_ROOT / parsed.path.removeprefix("/media/")
            if candidate.exists() and candidate.is_file():
                return candidate
        return None

    if value.startswith("/media/"):
        candidate = MEDIA_ROOT / value.removeprefix("/media/")
    elif value.startswith("media/"):
        candidate = MEDIA_ROOT / value.removeprefix("media/")
    elif "/" not in value and "." in value:
        candidate = MEDIA_ROOT / value
    else:
        candidate = Path(value)

    if candidate.exists() and candidate.is_file():
        return candidate

    return None


def _looks_like_telegram_file_id(value: str) -> bool:
    if not value:
        return False
    if "/" in value:
        return False
    if value.startswith("http://") or value.startswith("https://"):
        return False
    if "." in value:
        return False
    return len(value) >= 20


def _is_private_hostname(hostname: str) -> bool:
    if not hostname:
        return True
    if hostname in {"127.0.0.1", "localhost", "0.0.0.0", "backend"}:
        return True
    if hostname.endswith((".local", ".internal", ".lan")):
        return True
    if "." not in hostname:
        return True
    try:
        ip_addr = ipaddress.ip_address(hostname)
        return not ip_addr.is_global
    except ValueError:
        return False


def is_local_url(url: str) -> bool:
    parsed_url = urlparse(url)
    parsed_api = urlparse(API_URL)

    hostname = (parsed_url.hostname or "").lower()
    api_hostname = (parsed_api.hostname or "").lower()

    if _is_private_hostname(hostname):
        return True

    if api_hostname and hostname == api_hostname and _is_private_hostname(api_hostname):
        return True

    return False


def media_cache_key(photo_ref: str | None) -> str | None:
    return full_media_url(photo_ref)


async def get_lead_request(user_id: int) -> dict | None:
    context = lead_requests.get(user_id)
    if context is not None:
        return context.copy()

    context = await runtime_store.get_json(_lead_request_key(user_id))
    if not isinstance(context, dict):
        return None

    lead_requests[user_id] = context
    return context.copy()


async def set_lead_request(user_id: int, context: dict):
    clean_context = {**context}
    lead_requests[user_id] = clean_context
    await runtime_store.set_json(
        _lead_request_key(user_id),
        clean_context,
        LEAD_STATE_TTL_SECONDS,
    )


async def pop_lead_request(user_id: int) -> dict | None:
    context = lead_requests.pop(user_id, None)
    if context is not None:
        await runtime_store.delete(_lead_request_key(user_id))
        return context

    return await runtime_store.pop_json(_lead_request_key(user_id))


async def get_reminder_reply_context(user_id: int) -> dict | None:
    context = reminder_reply_waiting.get(user_id)
    if context is not None:
        return context.copy()

    context = await runtime_store.get_json(_reminder_reply_key(user_id))
    if not isinstance(context, dict):
        return None

    reminder_reply_waiting[user_id] = context
    return context.copy()


async def set_reminder_reply_context(user_id: int, context: dict):
    clean_context = {**context}
    reminder_reply_waiting[user_id] = clean_context
    await runtime_store.set_json(
        _reminder_reply_key(user_id),
        clean_context,
        REMINDER_STATE_TTL_SECONDS,
    )


async def pop_reminder_reply_context(user_id: int) -> dict | None:
    context = reminder_reply_waiting.pop(user_id, None)
    if context is not None:
        await runtime_store.delete(_reminder_reply_key(user_id))
        return context

    return await runtime_store.pop_json(_reminder_reply_key(user_id))


async def clear_reminder_reply_context(user_id: int):
    reminder_reply_waiting.pop(user_id, None)
    await runtime_store.delete(_reminder_reply_key(user_id))


async def is_consultation_waiting(user_id: int) -> bool:
    if consultation_waiting_question.get(user_id):
        return True

    cached = await runtime_store.get_text(_consultation_waiting_key(user_id))
    if cached == "1":
        consultation_waiting_question[user_id] = True
        return True

    return False


async def set_consultation_waiting(user_id: int):
    consultation_waiting_question[user_id] = True
    await runtime_store.set_text(
        _consultation_waiting_key(user_id),
        "1",
        LEAD_STATE_TTL_SECONDS,
    )


async def clear_consultation_waiting(user_id: int):
    consultation_waiting_question.pop(user_id, None)
    await runtime_store.delete(_consultation_waiting_key(user_id))


async def _set_reminder_schedule(user_id: int, chat_id: int, due_at: float):
    await runtime_store.set_json(
        _reminder_schedule_key(user_id),
        {"user_id": user_id, "chat_id": chat_id, "due_at": due_at},
        REMINDER_STATE_TTL_SECONDS,
    )


async def _clear_reminder_schedule(user_id: int):
    await runtime_store.delete(_reminder_schedule_key(user_id))


async def restore_pending_reminders(bot):
    schedules = await runtime_store.scan_json("bot:state:reminder_schedule:")
    for payload in schedules.values():
        if not isinstance(payload, dict):
            continue

        user_id = payload.get("user_id")
        chat_id = payload.get("chat_id")
        due_at = payload.get("due_at")
        if not isinstance(user_id, int) or not isinstance(chat_id, int):
            continue
        if not isinstance(due_at, (int, float)):
            continue
        if user_id in reminder_tasks:
            continue

        reminder_tasks[user_id] = asyncio.create_task(
            schedule_abandoned_reminder(user_id, chat_id, bot, due_at=float(due_at))
        )


async def _get_cached_media_file_id(photo_ref: str | None) -> str | None:
    key = media_cache_key(photo_ref)
    if not key:
        return None

    cached = media_file_id_cache.get(key)
    if cached:
        return cached

    cached = await runtime_store.get_text(_media_file_id_store_key(key))
    if not cached:
        return None

    media_file_id_cache[key] = cached
    return cached


async def remember_sent_photo(photo_ref: str | None, sent_message: Message):
    key = media_cache_key(photo_ref)
    if not key:
        return

    photo_sizes = getattr(sent_message, "photo", None)
    if not photo_sizes:
        return

    new_file_id = photo_sizes[-1].file_id
    if media_file_id_cache.get(key) == new_file_id:
        return

    media_file_id_cache[key] = new_file_id
    await runtime_store.set_text(
        _media_file_id_store_key(key),
        new_file_id,
        MEDIA_FILE_ID_TTL_SECONDS,
    )
    try:
        _persist_media_file_id_cache()
    except Exception:
        return


def _png_to_jpeg_bytes(content: bytes, filename: str) -> BufferedInputFile | None:
    try:
        with Image.open(BytesIO(content)) as image:
            image = ImageOps.exif_transpose(image)
            image.load()
            if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
                image = image.convert("RGBA")
                background = Image.new("RGB", image.size, (255, 255, 255))
                background.paste(image, mask=image.getchannel("A"))
                image = background
            elif image.mode != "RGB":
                image = image.convert("RGB")

            image.thumbnail(
                (TELEGRAM_IMAGE_MAX_SIZE, TELEGRAM_IMAGE_MAX_SIZE),
                Image.Resampling.LANCZOS,
            )

            buffer = BytesIO()
            image.save(
                buffer,
                format="JPEG",
                quality=TELEGRAM_JPEG_QUALITY,
                optimize=True,
                progressive=True,
            )
    except (UnidentifiedImageError, OSError):
        return None

    safe_name = f"{Path(filename).stem or 'image'}.jpg"
    return BufferedInputFile(buffer.getvalue(), filename=safe_name)


async def cancel_reminder_task(user_id: int):
    task = reminder_tasks.pop(user_id, None)
    if task and not task.done():
        task.cancel()
    await _clear_reminder_schedule(user_id)


async def touch_catalog_activity(
    user_id: int,
    bot,
    chat_id: int,
    *,
    sub_id: int | None = None,
    product_id: int | None = None,
    product_name: str | None = None,
):
    context = await get_lead_request(user_id) or {}
    context["chat_id"] = chat_id

    if sub_id is not None:
        context["sub_id"] = sub_id
    if product_id is not None:
        context["product_id"] = product_id
    if product_name is not None:
        context["product_name"] = product_name

    await asyncio.gather(
        set_lead_request(user_id, context),
        clear_reminder_reply_context(user_id),
        cancel_reminder_task(user_id),
    )
    reminder_tasks[user_id] = asyncio.create_task(
        schedule_abandoned_reminder(user_id, chat_id, bot)
    )


async def schedule_abandoned_reminder(user_id: int, chat_id: int, bot, due_at: float | None = None):
    current_task = asyncio.current_task()
    try:
        if due_at is None:
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
            except Exception:
                delay_minutes = DEFAULT_ABANDONED_REMINDER_DELAY_MINUTES
            due_at = time.time() + delay_minutes * 60

        await _set_reminder_schedule(user_id, chat_id, due_at)
        wait_seconds = max(0.0, due_at - time.time())
        if wait_seconds:
            await asyncio.sleep(wait_seconds)

        try:
            settings = await get_bot_settings()
            reminder_text = (
                settings.get("abandoned_reminder_message")
                or DEFAULT_ABANDONED_REMINDER_MESSAGE
            )
        except Exception:
            reminder_text = DEFAULT_ABANDONED_REMINDER_MESSAGE

        context = await get_lead_request(user_id)
        if not context:
            return

        sent = await bot.send_message(
            chat_id,
            f"{reminder_text}\n\nОтветьте на это сообщение, и я снова попрошу номер телефона.",
        )
        await set_reminder_reply_context(
            user_id,
            {
            **context,
            "prompt_message_id": sent.message_id,
            },
        )
    finally:
        if reminder_tasks.get(user_id) is current_task:
            reminder_tasks.pop(user_id, None)
            await _clear_reminder_schedule(user_id)


async def photo_payload(photo_ref: str | None):
    if not photo_ref:
        return None

    if _looks_like_telegram_file_id(photo_ref):
        return photo_ref

    cached_file_id = await _get_cached_media_file_id(photo_ref)
    if cached_file_id:
        return cached_file_id

    local_path = _resolve_local_media_path(photo_ref)
    if local_path:
        if local_path.suffix.lower() == ".png":
            try:
                content = await asyncio.to_thread(local_path.read_bytes)
            except Exception:
                return None
            converted = _png_to_jpeg_bytes(content, local_path.name)
            if converted:
                return converted
        return FSInputFile(local_path)

    value = full_media_url(photo_ref)
    if not value:
        return None

    if value.startswith("http://") or value.startswith("https://"):
        if _is_png_ref(value):
            filename = Path(value.split("?", 1)[0]).name or "image.png"
            try:
                content = await fetch_bytes(value, cache_seconds=300)
            except Exception:
                return None
            if not content:
                return None
            converted = _png_to_jpeg_bytes(content, filename)
            if converted:
                return converted

        if not is_local_url(value):
            return value

        filename = Path(value.split("?", 1)[0]).name or "image.jpg"
        try:
            content = await fetch_bytes(value, cache_seconds=300)
        except Exception:
            return None
        if not content:
            return None
        if _is_png_ref(value):
            converted = _png_to_jpeg_bytes(content, filename)
            if converted:
                return converted
        return BufferedInputFile(content, filename=filename)

    return value


def _is_png_ref(photo_ref: str | None) -> bool:
    if not photo_ref:
        return False
    value = str(photo_ref).strip().lower()
    if not value:
        return False
    value = value.split("?", 1)[0]
    return value.endswith(".png")


async def send_photo_with_fallback(
    message: Message,
    photo,
    *,
    caption: str | None = None,
    image_url: str | None = None,
    parse_mode: str | None = "Markdown",
    reply_markup=None,
):
    try:
        return await message.answer_photo(
            photo=photo,
            caption=caption,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
        )
    except Exception:
        if _is_png_ref(image_url):
            try:
                return await message.answer_document(
                    document=photo,
                    caption=caption,
                    parse_mode=parse_mode,
                    reply_markup=reply_markup,
                )
            except Exception:
                return None
        return None


async def safe_callback_answer(callback: CallbackQuery, text: str | None = None) -> bool:
    try:
        await callback.answer(
            text=text,
            request_timeout=CALLBACK_ACK_TIMEOUT_SECONDS,
        )
        return True
    except (TelegramNetworkError, TelegramServerError) as exc:
        logger.warning(
            "Callback ack failed for user_id=%s data=%s: %s",
            getattr(callback.from_user, "id", None),
            callback.data,
            exc,
        )
        return False
    except Exception:
        logger.debug("Unexpected callback ack failure for %s", callback.data, exc_info=True)
        return False


async def safe_delete_message(message: Message | None):
    if not message:
        return
    try:
        await message.delete()
    except Exception:
        return


async def send_subcategories_menu(callback: CallbackQuery, cat_id: int):
    subcategories = await get_subcategories_cached(cat_id)

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
    sub = subcategories_cache.get(sub_id, {})
    sub_image = sub.get("image_url")

    products_task = asyncio.create_task(get_products_cached(sub_id))
    photo_task = asyncio.create_task(photo_payload(sub_image)) if sub_image else None

    products = await products_task
    if not products:
        await callback.message.answer("❌ В этой подкатегории пока нет товаров")
        return

    sub_name = sub.get("name", "Подкатегория")
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
    photo = await photo_task if photo_task else None

    asyncio.create_task(safe_delete_message(callback.message))

    if photo:
        sent = await send_photo_with_fallback(
            callback.message,
            photo,
            caption=caption,
            image_url=sub_image,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
        if sent:
            await remember_sent_photo(sub_image, sent)
            return

    await callback.message.answer(caption, parse_mode="Markdown", reply_markup=keyboard)


async def send_product_card(callback: CallbackQuery, sub_id: int, product_id: int):
    products = await get_products_cached(sub_id)
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

    asyncio.create_task(safe_delete_message(callback.message))

    if photo:
        sent = await send_photo_with_fallback(
            callback.message,
            photo,
            caption=text,
            image_url=product.get("image_file_id"),
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
        if sent:
            await remember_sent_photo(product.get("image_file_id"), sent)
            return

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
