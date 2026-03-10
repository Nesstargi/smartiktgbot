# Release Checklist (SmartIKTG Bot)

## 1) Critical Before Release

- [ ] Rotate leaked Telegram token and issue a new one in BotFather.
- [ ] Rotate `JWT_SECRET_KEY` in production.
- [ ] Move production DB from SQLite to PostgreSQL.
- [ ] Add persistent storage for abandoned-lead state (currently in bot memory).

## 2) Security

- [x] `.env.example` sanitized (no real secrets/tokens).
- [x] `.env` ignored by git.
- [ ] Add login rate limiting for `/admin/auth/login`.
- [ ] Restrict CORS origins for production domain(s).
- [ ] Add request size limits and upload validation hardening.

## 3) API Robustness

- [x] `/api/leads` now validated with Pydantic schema.
- [x] Bot callback handlers acknowledge button presses (`callback.answer()`).
- [ ] Add global API error handler and consistent error response format.
- [ ] Add idempotency/duplicate-protection for leads.

## 4) Observability & Operations

- [x] Added `GET /health` endpoint.
- [ ] Add structured logging (json) with request/user context.
- [ ] Add uptime/alert monitoring (health checks, restart alerts).
- [ ] Add backup policy for DB + `backend/media`.

## 5) Data & Migrations

- [ ] Replace runtime SQLite `ALTER TABLE` migrations with Alembic.
- [ ] Add migration history and rollback strategy.

## 6) Bot UX/Performance

- [x] Reused HTTP session + response caching in bot API client.
- [x] Added media caching and Telegram `file_id` reuse where applicable.
- [ ] Persist media cache/state across restarts (optional optimization).
- [ ] Add fallback behavior if Telegram media send fails repeatedly.

## 7) Testing

- [ ] Add backend smoke tests (auth, catalog CRUD, leads, bot settings).
- [ ] Add bot flow integration tests (category -> subcategory -> product -> lead).
- [ ] Add pre-release script: lint + tests + build.

## 8) Deployment

- [ ] Add Dockerfiles + docker-compose for reproducible deploy.
- [ ] Add production runbook (env vars, start order, rollback, backup restore).

---

## Current Project Status Summary

- Ready for controlled pilot with manual supervision.
- Not yet ready for unattended production due to missing persistence, migrations, and ops controls.
