from fastapi import FastAPI
from backend.database import engine, Base
from backend.api import router

# Создаём таблицы (если их нет)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SmartIKTG Backend")
app.include_router(router)
