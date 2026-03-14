# SmartIKTG Bot

SmartIKTG Bot is a small monorepo with three runtime parts:

- `backend/`: FastAPI API for public bot data and the admin panel
- `bot/`: Telegram bot built on `aiogram`
- `admin-panel/`: React + Vite admin UI

## Local setup

1. Create `.env` from `.env.example` and fill in real values.
2. Install Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

3. Install frontend dependencies:

```powershell
Set-Location admin-panel
npm install
Set-Location ..
```

4. Apply database migrations:

```powershell
python -m alembic upgrade head
```

5. Create the first admin user:

```powershell
python backend/scripts/create_admin.py --email admin@example.com --password change-me
```

6. Start all local services:

```powershell
.\start.ps1
```

The startup script now runs `python -m alembic upgrade head` before the backend server.

## Docker

```powershell
docker compose up --build
```

The Docker stack starts PostgreSQL, Redis, backend, bot, and the admin panel. The backend container applies Alembic migrations before launching Uvicorn.

## Bot Delivery Modes

- `BOT_DELIVERY_MODE=polling`: the `bot` service consumes updates directly from Telegram.
- `BOT_DELIVERY_MODE=webhook`: the FastAPI backend receives updates on `TELEGRAM_WEBHOOK_PATH`, and the standalone `bot` process stays idle.
- If the server is reachable only by bare IP over plain `http`, keep `BOT_DELIVERY_MODE=polling` for now. Webhook should be enabled only after you have public `https` access.

To enable webhook mode, set:

```powershell
BOT_DELIVERY_MODE=webhook
TELEGRAM_WEBHOOK_BASE_URL=https://your-domain.example
TELEGRAM_WEBHOOK_PATH=/telegram/webhook
TELEGRAM_WEBHOOK_SECRET=your-long-random-secret
```

The public HTTPS URL exposed to Telegram becomes `TELEGRAM_WEBHOOK_BASE_URL + TELEGRAM_WEBHOOK_PATH`.

## Notes

- Legacy SQLite databases created by older versions can be upgraded with `python -m alembic upgrade head`.
- `backend/main.py` no longer creates or alters tables automatically on import.
- `backend/media/` is kept in the repository as an empty runtime directory placeholder.
- The bot uses Redis for shared cache and dialog state when `REDIS_URL` is set; if Redis is unavailable, it falls back to local in-memory cache.
