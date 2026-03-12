from pathlib import Path

# backend/api/admin/users.py
p = Path("backend/api/admin/users.py")
t = p.read_text(encoding="utf-8-sig")
if "from sqlalchemy import func" not in t:
    t = t.replace(
        "from fastapi import APIRouter, Depends, HTTPException\nfrom sqlalchemy.orm import Session\n",
        "from fastapi import APIRouter, Depends, HTTPException\nfrom sqlalchemy import func\nfrom sqlalchemy.orm import Session\n",
    )
t = t.replace(
    "    existing = db.query(User).filter(User.email == data.email).first()\n"
    "    if existing:\n"
    "        raise HTTPException(status_code=400, detail=\"Email already exists\")\n\n"
    "    user = User(email=data.email, hashed_password=hash_password(data.password), is_active=True)\n",
    "    normalized_email = data.email.strip().lower()\n\n"
    "    existing = db.query(User).filter(func.lower(User.email) == normalized_email).first()\n"
    "    if existing:\n"
    "        raise HTTPException(status_code=400, detail=\"Email already exists\")\n\n"
    "    user = User(email=normalized_email, hashed_password=hash_password(data.password), is_active=True)\n",
)
p.write_text(t, encoding="utf-8")

# backend/api/admin/auth.py
p = Path("backend/api/admin/auth.py")
t = p.read_text(encoding="utf-8-sig")
t = t.replace(
    "    key = _rate_limit_key(request, data.email)\n",
    "    normalized_email = data.email.strip().lower()\n    key = _rate_limit_key(request, normalized_email)\n",
)
t = t.replace(
    "    user = db.query(User).filter(User.email == data.email).first()\n",
    "    user = db.query(User).filter(User.email.ilike(normalized_email)).first()\n",
)
p.write_text(t, encoding="utf-8")

# bot/handlers/catalog_common.py
p = Path("bot/handlers/catalog_common.py")
t = p.read_text(encoding="utf-8-sig")
if "from urllib.parse import urlparse" not in t:
    t = t.replace(
        "import asyncio\nfrom pathlib import Path\n",
        "import asyncio\nfrom pathlib import Path\nfrom urllib.parse import urlparse\n",
    )
t = t.replace(
    "def full_media_url(path_or_url: str | None):\n"
    "    if not path_or_url:\n"
    "        return None\n"
    "    if path_or_url.startswith(\"http://\") or path_or_url.startswith(\"https://\"):\n"
    "        return path_or_url\n"
    "    if path_or_url.startswith(\"/\"):\n"
    "        return f\"{API_URL}{path_or_url}\"\n"
    "    return path_or_url\n\n\n"
    "def is_local_url(url: str) -> bool:\n"
    "    return \"127.0.0.1\" in url or \"localhost\" in url\n",
    "def full_media_url(path_or_url: str | None):\n"
    "    if not path_or_url:\n"
    "        return None\n"
    "    if path_or_url.startswith(\"http://\") or path_or_url.startswith(\"https://\"):\n"
    "        return path_or_url\n"
    "    if path_or_url.startswith(\"/\"):\n"
    "        return f\"{API_URL}{path_or_url}\"\n\n"
    "    # Поддержка старых записей, где в БД хранится только имя файла.\n"
    "    if \"/\" not in path_or_url:\n"
    "        return f\"{API_URL}/media/{path_or_url}\"\n\n"
    "    return f\"{API_URL}/{path_or_url.lstrip('/')}\"\n\n\n"
    "def is_local_url(url: str) -> bool:\n"
    "    parsed_url = urlparse(url)\n"
    "    parsed_api = urlparse(API_URL)\n\n"
    "    hostname = (parsed_url.hostname or \"\").lower()\n"
    "    api_hostname = (parsed_api.hostname or \"\").lower()\n\n"
    "    if hostname in {\"127.0.0.1\", \"localhost\", \"0.0.0.0\", \"backend\"}:\n"
    "        return True\n\n"
    "    if api_hostname and hostname == api_hostname:\n"
    "        return True\n\n"
    "    return False\n",
)
p.write_text(t, encoding="utf-8")

# admin-panel/src/utils/media.js
p = Path("admin-panel/src/utils/media.js")
t = p.read_text(encoding="utf-8-sig")
t = t.replace(
    "  const base = (import.meta.env.VITE_API_URL || \"http://localhost:8000\").replace(/\\/$/, \"\");\n"
    "  const path = pathOrUrl.startsWith(\"/\") ? pathOrUrl : `/${pathOrUrl}`;\n"
    "  return `${base}${path}`;\n",
    "  const base = (import.meta.env.VITE_API_URL || \"http://localhost:8000\").replace(/\\/$/, \"\");\n"
    "  const normalized = pathOrUrl.includes(\"/\") ? pathOrUrl : `/media/${pathOrUrl}`;\n"
    "  const path = normalized.startsWith(\"/\") ? normalized : `/${normalized}`;\n"
    "  return `${base}${path}`;\n",
)
p.write_text(t, encoding="utf-8")

print("Patched.")
