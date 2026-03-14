import asyncio
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from bot.runtime import (
    delete_webhook,
    get_webhook_url,
    has_bot_token,
    is_webhook_mode,
    shutdown_bot_runtime,
    startup_bot_runtime,
)

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)


async def main():
    if not has_bot_token():
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    if is_webhook_mode():
        logger.info(
            "BOT_DELIVERY_MODE=webhook. Telegram updates are handled by backend webhook at %s",
            get_webhook_url() or "TELEGRAM_WEBHOOK_BASE_URL + TELEGRAM_WEBHOOK_PATH",
        )
        await asyncio.Event().wait()
        return

    bot, dispatcher = await startup_bot_runtime()
    if bot is None:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    await delete_webhook(drop_pending_updates=False)

    try:
        await dispatcher.start_polling(
            bot,
            allowed_updates=dispatcher.resolve_used_update_types(),
        )
    finally:
        await shutdown_bot_runtime()


if __name__ == "__main__":
    asyncio.run(main())
