from aiogram import Router

from bot.handlers.catalog_handlers import router as catalog_handlers_router

router = Router()
router.include_router(catalog_handlers_router)
