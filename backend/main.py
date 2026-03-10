from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

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
)
from backend.config import CORS_ALLOW_ORIGINS
from backend.database import Base, SessionLocal, engine
from backend.models.role import Role
from backend.models.user_role import UserRole


Base.metadata.create_all(bind=engine)


def _ensure_sqlite_migrations():
    with engine.begin() as conn:
        promo_cols = {
            row[1]
            for row in conn.execute(text("PRAGMA table_info(promotions)")).fetchall()
        }
        if "image_url" not in promo_cols:
            conn.execute(text("ALTER TABLE promotions ADD COLUMN image_url VARCHAR"))

        sub_cols = {
            row[1]
            for row in conn.execute(text("PRAGMA table_info(subcategories)")).fetchall()
        }
        if "image_url" not in sub_cols:
            conn.execute(text("ALTER TABLE subcategories ADD COLUMN image_url VARCHAR"))

        settings_cols = {
            row[1]
            for row in conn.execute(text("PRAGMA table_info(bot_settings)")).fetchall()
        }
        if "abandoned_reminder_message" not in settings_cols:
            conn.execute(
                text(
                    "ALTER TABLE bot_settings ADD COLUMN abandoned_reminder_message VARCHAR "
                    "DEFAULT 'Вы смотрели товары, но не оставили заявку. Ответьте на это сообщение, и мы поможем оформить заказ.'"
                )
            )
        if "abandoned_reminder_delay_minutes" not in settings_cols:
            conn.execute(
                text(
                    "ALTER TABLE bot_settings ADD COLUMN abandoned_reminder_delay_minutes INTEGER DEFAULT 30"
                )
            )
        if "consultation_phone" not in settings_cols:
            conn.execute(
                text(
                    "ALTER TABLE bot_settings ADD COLUMN consultation_phone VARCHAR DEFAULT '+7 (000) 000-00-00'"
                )
            )
        if "consultation_message" not in settings_cols:
            conn.execute(
                text(
                    "ALTER TABLE bot_settings ADD COLUMN consultation_message VARCHAR "
                    "DEFAULT '📞 Для консультации позвоните по номеру: {phone}\n\n✍️ Или задайте вопрос в сообщении ниже.'"
                )
            )
        if "consultation_contact_prompt" not in settings_cols:
            conn.execute(
                text(
                    "ALTER TABLE bot_settings ADD COLUMN consultation_contact_prompt VARCHAR "
                    "DEFAULT 'Спасибо, вопрос получил. Теперь нажмите кнопку ниже и поделитесь номером телефона:'"
                )
            )
        if "about_message" not in settings_cols:
            conn.execute(
                text(
                    "ALTER TABLE bot_settings ADD COLUMN about_message VARCHAR "
                    "DEFAULT 'О компании: мы помогаем подобрать решение под ваш запрос.'"
                )
            )

        leads_cols = {
            row[1] for row in conn.execute(text("PRAGMA table_info(leads)")).fetchall()
        }
        if "created_at" not in leads_cols:
            # SQLite cannot add a column with a non-constant default.
            conn.execute(text("ALTER TABLE leads ADD COLUMN created_at DATETIME"))
            conn.execute(text("UPDATE leads SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL"))


def _bootstrap_super_admin_role():
    db = SessionLocal()
    try:
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if not admin_role:
            admin_role = Role(name="admin")
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)

        super_admin_role = db.query(Role).filter(Role.name == "super_admin").first()
        if not super_admin_role:
            super_admin_role = Role(name="super_admin")
            db.add(super_admin_role)
            db.commit()
            db.refresh(super_admin_role)

        has_super_admin = (
            db.query(UserRole)
            .filter(UserRole.role_id == super_admin_role.id)
            .first()
        )
        if has_super_admin:
            return

        first_admin = (
            db.query(UserRole)
            .filter(UserRole.role_id == admin_role.id)
            .order_by(UserRole.user_id.asc())
            .first()
        )
        if first_admin:
            db.add(UserRole(user_id=first_admin.user_id, role_id=super_admin_role.id))
            db.commit()
    finally:
        db.close()


_ensure_sqlite_migrations()
_bootstrap_super_admin_role()

app = FastAPI(title="SmartIKTG Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Public API
app.include_router(categories_router, prefix="/api", tags=["categories"])
app.include_router(subcategories_router, prefix="/api", tags=["subcategories"])
app.include_router(products_router, prefix="/api", tags=["products"])
app.include_router(leads_router, prefix="/api", tags=["leads"])
app.include_router(promotions_router, prefix="/api", tags=["promotions"])
app.include_router(bot_settings_router, prefix="/api", tags=["bot-settings"])

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

app.mount("/media", StaticFiles(directory="backend/media"), name="media")


@app.get("/health")
def health():
    return {"status": "ok"}
