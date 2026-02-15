from fastapi import FastAPI
from backend.database import engine
from backend.models import Base
from backend.api import router

Base.metadata.create_all(bind=engine)

app = FastAPI()


app.include_router(router)


@app.get("/")
def root():
    return {"status": "ok"}
