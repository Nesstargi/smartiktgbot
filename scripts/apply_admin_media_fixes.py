#!/usr/bin/env python3
"""Apply known admin/media fixes to project files.

Usage:
  python scripts/apply_admin_media_fixes.py        # apply changes
  python scripts/apply_admin_media_fixes.py --check  # show if changes are needed
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Tuple

ROOT = Path(__file__).resolve().parents[1]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def replace_block(text: str, old: str, new: str) -> Tuple[str, bool]:
    if new in text:
        return text, False
    if old in text:
        return text.replace(old, new), True
    return text, False


def ensure_insertion(text: str, needle: str, insertion_after: str) -> Tuple[str, bool]:
    if needle in text:
        return text, False
    if insertion_after in text:
        idx = text.index(insertion_after) + len(insertion_after)
        return text[:idx] + needle + text[idx:], True
    return text, False


def patch_users_py(content: str) -> Tuple[str, int]:
    changes = 0

    content, changed = ensure_insertion(
        content,
        "from sqlalchemy import func\n",
        "from fastapi import APIRouter, Depends, HTTPException\n",
    )
    changes += int(changed)

    old = (
        "    existing = db.query(User).filter(User.email == data.email).first()\n"
        "    if existing:\n"
        "        raise HTTPException(status_code=400, detail=\"Email already exists\")\n\n"
        "    user = User(email=data.email, hashed_password=hash_password(data.password), is_active=True)\n"
    )
    new = (
        "    normalized_email = data.email.strip().lower()\n\n"
        "    existing = db.query(User).filter(func.lower(User.email) == normalized_email).first()\n"
        "    if existing:\n"
        "        raise HTTPException(status_code=400, detail=\"Email already exists\")\n\n"
        "    user = User(email=normalized_email, hashed_password=hash_password(data.password), is_active=True)\n"
    )
    content, changed = replace_block(content, old, new)
    changes += int(changed)
    return content, changes


def patch_auth_py(content: str) -> Tuple[str, int]:
    changes = 0
    content, changed = replace_block(
        content,
        "    key = _rate_limit_key(request, data.email)\n",
        "    normalized_email = data.email.strip().lower()\n    key = _rate_limit_key(request, normalized_email)\n",
    )
    changes += int(changed)

    content, changed = replace_block(
        content,
        "    user = db.query(User).filter(User.email == data.email).first()\n",
        "    user = db.query(User).filter(User.email.ilike(normalized_email)).first()\n",
    )
    changes += int(changed)
    return content, changes


def patch_catalog_common_py(content: str) -> Tuple[str, int]:
    changes = 0

    content, changed = ensure_insertion(
        content,
        "from urllib.parse import urlparse\n",
        "from pathlib import Path\n",
    )
    changes += int(changed)

    old = (
        "def full_media_url(path_or_url: str | None):\n"
        "    if not path_or_url:\n"
        "        return None\n"
        "    if path_or_url.startswith(\"http://\") or path_or_url.startswith(\"https://\"):\n"
        "        return path_or_url\n"
        "    if path_or_url.startswith(\"/\"):\n"
        "        return f\"{API_URL}{path_or_url}\"\n"
        "    return path_or_url\n\n\n"
        "def is_local_url(url: str) -> bool:\n"
        "    return \"127.0.0.1\" in url or \"localhost\" in url\n"
    )
    new = (
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
        "    return False\n"
    )
    content, changed = replace_block(content, old, new)
    changes += int(changed)
    return content, changes


def patch_media_js(content: str) -> Tuple[str, int]:
    changes = 0
    old = (
        '  const base = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\\/$/, "");\n'
        '  const path = pathOrUrl.startsWith("/") ? pathOrUrl : `/${pathOrUrl}`;\n'
        '  return `${base}${path}`;\n'
    )
    new = (
        '  const base = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\\/$/, "");\n'
        '  const normalized = pathOrUrl.includes("/") ? pathOrUrl : `/media/${pathOrUrl}`;\n'
        '  const path = normalized.startsWith("/") ? normalized : `/${normalized}`;\n'
        '  return `${base}${path}`;\n'
    )
    content, changed = replace_block(content, old, new)
    changes += int(changed)
    return content, changes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Only report if patching is needed")
    args = parser.parse_args()

    files = {
        ROOT / "backend/api/admin/users.py": patch_users_py,
        ROOT / "backend/api/admin/auth.py": patch_auth_py,
        ROOT / "bot/handlers/catalog_common.py": patch_catalog_common_py,
        ROOT / "admin-panel/src/utils/media.js": patch_media_js,
    }

    changed_paths: list[Path] = []

    for path, patcher in files.items():
        original = read_text(path)
        updated, changes = patcher(original)
        if changes > 0 and updated != original:
            changed_paths.append(path)
            if not args.check:
                path.write_text(updated, encoding="utf-8")

    if changed_paths:
        print("Need changes:" if args.check else "Updated files:")
        for p in changed_paths:
            print("-", p.relative_to(ROOT))
        return 1 if args.check else 0

    print("No changes needed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
