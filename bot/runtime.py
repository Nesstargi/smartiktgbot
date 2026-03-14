from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.types import Update
from dotenv import load_dotenv

from bot.api_client import close_http_session
from bot.handlers.catalog import router as catalog_router
from bot.handlers.catalog_common import (
    restore_pending_reminders,
    schedule_catalog_warmup,
    shutdown_background_tasks,
)
from bot.handlers.menu import router as menu_router
from bot.runtime_store import runtime_store

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
BOT_DELIVERY_MODE = (os.getenv("BOT_DELIVERY_MODE", "polling").strip().lower() or "polling")
TELEGRAM_WEBHOOK_BASE_URL = os.getenv("TELEGRAM_WEBHOOK_BASE_URL", "").strip().rstrip("/")
TELEGRAM_WEBHOOK_PATH = (os.getenv("TELEGRAM_WEBHOOK_PATH", "/telegram/webhook").strip() or "/telegram/webhook")
if not TELEGRAM_WEBHOOK_PATH.startswith("/"):
    TELEGRAM_WEBHOOK_PATH = f"/{TELEGRAM_WEBHOOK_PATH}"
TELEGRAM_WEBHOOK_SECRET = os.getenv("TELEGRAM_WEBHOOK_SECRET", "").strip()
TELEGRAM_WEBHOOK_DROP_PENDING_UPDATES = os.getenv(
    "TELEGRAM_WEBHOOK_DROP_PENDING_UPDATES",
    "false",
).strip().lower() in {"1", "true", "yes", "on"}

_bot: Bot | None = None
_dispatcher: Dispatcher | None = None
_runtime_started = False


def has_bot_token() -> bool:
    return bool(TOKEN)


def is_webhook_mode() -> bool:
    return BOT_DELIVERY_MODE == "webhook"


def is_polling_mode() -> bool:
    return not is_webhook_mode()


def get_webhook_path() -> str:
    return TELEGRAM_WEBHOOK_PATH


def get_webhook_url() -> str:
    if not TELEGRAM_WEBHOOK_BASE_URL:
        return ""
    return f"{TELEGRAM_WEBHOOK_BASE_URL}{TELEGRAM_WEBHOOK_PATH}"


def _validate_webhook_config():
    if not has_bot_token():
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
    if not TELEGRAM_WEBHOOK_BASE_URL:
        raise RuntimeError("TELEGRAM_WEBHOOK_BASE_URL is not set for webhook mode")
    if not TELEGRAM_WEBHOOK_SECRET:
        raise RuntimeError("TELEGRAM_WEBHOOK_SECRET is not set for webhook mode")


def _build_dispatcher() -> Dispatcher:
    dispatcher = Dispatcher()
    dispatcher.include_router(menu_router)
    dispatcher.include_router(catalog_router)
    return dispatcher


def get_bot_instance() -> Bot | None:
    global _bot
    if not has_bot_token():
        return None
    if _bot is None:
        _bot = Bot(token=TOKEN)
    return _bot


def get_dispatcher() -> Dispatcher:
    global _dispatcher
    if _dispatcher is None:
        _dispatcher = _build_dispatcher()
    return _dispatcher


async def startup_bot_runtime() -> tuple[Bot | None, Dispatcher]:
    global _runtime_started

    dispatcher = get_dispatcher()
    bot = get_bot_instance()
    await runtime_store.initialize()

    if bot is not None and not _runtime_started:
        await restore_pending_reminders(bot)
        schedule_catalog_warmup()
        _runtime_started = True

    return bot, dispatcher


async def shutdown_bot_runtime():
    global _bot, _runtime_started

    await shutdown_background_tasks()
    await close_http_session()
    await runtime_store.close()

    if _bot is not None:
        try:
            await _bot.session.close()
        except Exception:
            logger.debug("Bot session close failed", exc_info=True)
    _bot = None

    _runtime_started = False


async def configure_webhook():
    _validate_webhook_config()

    bot, dispatcher = await startup_bot_runtime()
    if bot is None:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    await bot.set_webhook(
        url=get_webhook_url(),
        allowed_updates=dispatcher.resolve_used_update_types(),
        drop_pending_updates=TELEGRAM_WEBHOOK_DROP_PENDING_UPDATES,
        secret_token=TELEGRAM_WEBHOOK_SECRET,
    )
    logger.info("Telegram webhook configured for %s", get_webhook_url())


async def delete_webhook(drop_pending_updates: bool = False):
    bot = get_bot_instance()
    if bot is None:
        return

    await bot.delete_webhook(drop_pending_updates=drop_pending_updates)
    logger.info("Telegram webhook deleted")


def webhook_secret_is_valid(secret: str | None) -> bool:
    if not TELEGRAM_WEBHOOK_SECRET:
        return True
    return secret == TELEGRAM_WEBHOOK_SECRET


async def process_webhook_update(payload: dict[str, Any]):
    bot, dispatcher = await startup_bot_runtime()
    if bot is None:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    update = Update.model_validate(payload, context={"bot": bot})
    await dispatcher.feed_webhook_update(bot, update)
