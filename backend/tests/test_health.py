import os
from pathlib import Path


TEST_DB_PATH = Path(__file__).resolve().parent / ".test_db.sqlite3"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH.as_posix()}"

from backend.main import health


def test_health():
    assert health() == {"status": "ok"}
