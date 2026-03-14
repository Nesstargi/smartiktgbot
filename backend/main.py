from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.api.admin import (
    auth_router,
    bot_settings_router as admin_bot_settings_router,
    categories_router as admin_categories_router,
    dashboard_router,
    leads_router as admin_leads_router,
    notifications_router as admin_notifications_router,
    products_router as admin_products_router,
    promotions_router as admin_promotions_router,
    roles_router,
    subcategories_router as admin_subcategories_router,
    upload_router,
    users_router,
)
from backend.api.public import (
    bot_settings_router,
    categories_router,
    leads_router,
    products_router,
    promotions_router,
    subcategories_router,
    telegram_router,
)
from backend.bootstrap import bootstrap_default_roles
from backend.config import CORS_ALLOW_ORIGINS
from backend.media_static import MediaStaticFiles
from bot.runtime import configure_webhook, is_webhook_mode, shutdown_bot_runtime


MEDIA_DIR = Path(__file__).resolve().parent / "media"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)


def _error_code_for_status(status_code: int) -> str:
    codes = {
        400: "bad_request",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        409: "conflict",
        422: "validation_error",
        429: "rate_limited",
        503: "service_unavailable",
    }
    return codes.get(status_code, f"http_{status_code}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    bootstrap_default_roles()
    if is_webhook_mode():
        await configure_webhook()
    yield
    if is_webhook_mode():
        await shutdown_bot_runtime()


app = FastAPI(title="SmartIKTG Backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count"],
)

# Public API
app.include_router(categories_router, prefix="/api", tags=["categories"])
app.include_router(subcategories_router, prefix="/api", tags=["subcategories"])
app.include_router(products_router, prefix="/api", tags=["products"])
app.include_router(leads_router, prefix="/api", tags=["leads"])
app.include_router(promotions_router, prefix="/api", tags=["promotions"])
app.include_router(bot_settings_router, prefix="/api", tags=["bot-settings"])
app.include_router(telegram_router, tags=["telegram"])

# Admin API
app.include_router(auth_router, prefix="/admin/auth", tags=["admin"])
app.include_router(upload_router, prefix="/admin/upload", tags=["admin"])
app.include_router(admin_products_router, prefix="/admin/products", tags=["admin"])
app.include_router(admin_categories_router, prefix="/admin/categories", tags=["admin"])
app.include_router(
    admin_subcategories_router, prefix="/admin/subcategories", tags=["admin"]
)
app.include_router(admin_promotions_router, prefix="/admin/promotions", tags=["admin"])
app.include_router(
    admin_notifications_router, prefix="/admin/notifications", tags=["admin"]
)
app.include_router(
    admin_bot_settings_router,
    prefix="/admin/bot-settings",
    tags=["admin"],
)
app.include_router(admin_leads_router, prefix="/admin/leads", tags=["admin"])
app.include_router(users_router, prefix="/admin/users", tags=["admin"])
app.include_router(roles_router, prefix="/admin/roles", tags=["admin"])
app.include_router(dashboard_router, prefix="/admin/dashboard", tags=["admin"])

app.mount("/media", MediaStaticFiles(directory=str(MEDIA_DIR)), name="media")


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    content = {
        "detail": exc.detail,
        "code": _error_code_for_status(exc.status_code),
        "path": request.url.path,
    }
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(content),
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    content = {
        "detail": errors,
        "code": "validation_error",
        "errors": errors,
        "path": request.url.path,
    }
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder(content),
    )


@app.get("/health")
def health():
    return {"status": "ok"}
