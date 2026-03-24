# SmartIKTG Deployment Runbook

## Current deployment decision

Given the server details received on March 20, 2026:

- CPU: AMD Ryzen 5 5600
- RAM: 48 GB
- OS: Windows Server 2022
- Docker: available
- Domain: not configured
- Database: PostgreSQL can be installed
- Firewall: must stay enabled

The recommended first production rollout is:

- deploy from Docker Compose
- use PostgreSQL
- keep `BOT_DELIVERY_MODE=polling`
- keep backend private on `127.0.0.1:8000`
- expose only the admin panel port if browser access is needed

This matches the current constraint of IP-only access without public HTTPS.

## Service layout

The stack contains:

- `postgres`: main production database
- `redis`: bot cache and state storage
- `backend`: FastAPI API and media
- `bot`: Telegram bot process
- `admin`: React admin panel behind Nginx

The admin Nginx now proxies these backend paths internally:

- `/api/*`
- `/admin/*`
- `/media/*`
- `/telegram/*`
- `/health`

That means the browser can work through the admin panel origin, and the backend port does not need to be opened publicly.

## Recommended ports

Keep these ports closed externally:

- `8000/tcp`
- `5432/tcp`
- `6379/tcp`

Open only if needed:

- `5173/tcp` for the admin panel over bare IP

If the admin panel is used only through RDP or VPN, do not open `5173/tcp` publicly either.

## Security note

Running the admin panel over public bare `http://IP:5173` is acceptable only for a controlled pilot or for private-network access. It is not a good long-term public setup because admin authentication would travel without HTTPS.

Safer options:

- access admin only from RDP/VPN/private network
- later attach a domain and HTTPS

## Required `.env` values for the first server rollout

Minimum production values:

```env
JWT_SECRET_KEY=<long-random-secret>
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

POSTGRES_DB=smartiktg
POSTGRES_USER=smartiktg
POSTGRES_PASSWORD=<strong-password>
DATABASE_URL=postgresql+psycopg2://smartiktg:<strong-password>@postgres:5432/smartiktg

CORS_ALLOW_ORIGINS=http://SERVER_IP:5173

TELEGRAM_BOT_TOKEN=<real-bot-token>
BOT_API_TOKEN=<long-random-shared-token>
BOT_DELIVERY_MODE=polling
BACKEND_URL=http://backend:8000
REDIS_URL=redis://redis:6379/0
REDIS_PREFIX=smartiktg

TELEGRAM_LEADS_CHAT_ID=<optional-chat-id>
VITE_API_URL=/
```

If the admin panel is later moved to port `80`, change `CORS_ALLOW_ORIGINS` to `http://SERVER_IP`.

## First deploy steps on the server

1. Copy the project to the server.
2. Create a production `.env`.
3. Make sure Docker is using Linux containers.
4. Run:

```powershell
docker compose up -d --build
```

5. Create the first admin user:

```powershell
docker compose exec backend python backend/scripts/create_admin.py --email admin@example.com --password change-me
```

6. Check health:

```powershell
curl http://127.0.0.1:8000/health
```

7. If browser access is required, open only `5173/tcp` in Windows Firewall.

## Recommended git-based deploy flow

For ongoing updates, stop using archive uploads and switch the server to a normal git working copy.

Recommended day-to-day flow:

1. Make changes locally.
2. Commit and push to `origin/main`.
3. On the server, open the project directory and run:

```powershell
.\scripts\deploy_server.ps1
```

What this script does:

- checks that the folder is a git repository
- stops if there are tracked local changes on the server
- runs `git fetch` and `git pull --ff-only`
- runs `docker compose up -d --build`
- shows `docker compose ps`

If you want to preview commands first:

```powershell
.\scripts\deploy_server.ps1 -DryRun
```

If the application runs inside an Ubuntu VM, use:

```bash
chmod +x ./scripts/deploy_server.sh
./scripts/deploy_server.sh
```

## How to move the current archive-based server copy to git

Use this once on the server to replace the archive copy with a git-managed folder.

1. Open PowerShell in the current project folder.
2. Stop the running stack:

```powershell
docker compose down
```

3. Back up runtime data that must survive the switch:

- `.env`
- `backend\media`
- `pgdata`

4. Rename the current folder so you still have a rollback copy. Example:

```powershell
Set-Location C:\
Rename-Item .\smartiktgbot .\smartiktgbot_archive_2026-03-25
```

5. Clone the repository fresh:

```powershell
git clone https://github.com/Nesstargi/smartiktgbot.git C:\smartiktgbot
```

6. Copy back your production files:

- `.env` into `C:\smartiktgbot\.env`
- media files into `C:\smartiktgbot\backend\media`
- PostgreSQL data into `C:\smartiktgbot\pgdata`

7. Go into the new folder and deploy:

```powershell
Set-Location C:\smartiktgbot
.\scripts\deploy_server.ps1
```

If something goes wrong, you still have the renamed archive folder as a rollback point.

Ubuntu VM example:

```bash
cd /opt
sudo mv smartiktgbot smartiktgbot_archive_2026-03-25
git clone https://github.com/Nesstargi/smartiktgbot.git /opt/smartiktgbot
sudo cp /opt/smartiktgbot_archive_2026-03-25/.env /opt/smartiktgbot/.env
sudo cp -a /opt/smartiktgbot_archive_2026-03-25/backend/media/. /opt/smartiktgbot/backend/media/
sudo cp -a /opt/smartiktgbot_archive_2026-03-25/pgdata/. /opt/smartiktgbot/pgdata/
cd /opt/smartiktgbot
chmod +x ./scripts/deploy_server.sh
./scripts/deploy_server.sh
```

## GitHub access on the server

If the repository is private, the server must have access before `git clone` or `git pull` will work.

Common options:

- HTTPS + Git Credential Manager
- HTTPS + Personal Access Token
- SSH key attached to the repository or organization

For a simple Windows Server setup, HTTPS with Git Credential Manager is usually the easiest path.

## What we do locally

During development we can continue to work locally:

- local backend + bot + admin via `.\start.ps1`
- SQLite is acceptable for development
- production target remains Docker + PostgreSQL

This keeps development fast and avoids touching the customer server until the build is ready.

## When to switch to webhook mode

Switch from polling to webhook only after all of the following are true:

- a public domain exists
- HTTPS is configured
- port `443/tcp` is open
- `TELEGRAM_WEBHOOK_BASE_URL` points to the public HTTPS URL

At that point:

- set `BOT_DELIVERY_MODE=webhook`
- keep `/telegram/webhook` proxied to backend
- optionally stop exposing the admin panel on a custom high port and move to `443`

## Backups

Back up at minimum:

- `./pgdata`
- `./backend/media`
- production `.env` stored securely outside the server as well
