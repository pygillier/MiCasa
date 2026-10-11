# MiCasa v2

Single-user startpage: links grouped in categories, Uptime Kuma status dots, weather sidebar, OIDC-protected admin.
Visual reference: `mockups/Startpage.dc.html` (Nocturne design system in `mockups/_ds/`).

## Stack
- `backend/` — Flask, Flask-SQLAlchemy, Flask-Migrate, Authlib (OIDC + PKCE with PocketID), Flask-APScheduler (SQLAlchemy job store), `uptime-kuma-api2`. SQLite.
- `frontend/` — Next.js (App Router, TypeScript). Proxies `/api/*` to Flask (same origin).
- Tooling: `mise` (versions, see `mise.toml`) and `task` (see `Taskfile.yml`). Run `task --list`.

## Backend layout (`backend/app/`)
The root holds technical plumbing only; functional code lives in `features/`.
- Root (tech): `__init__.py` (`create_app`), `config.py`, `extensions.py`, `logs.py`, `models.py` (shared schema), `settings.py` (DB-backed settings), `auth.py` (OIDC client, `login_required`), `validation.py`.
- `blueprints/` — HTTP layer, one module per concern exposing `bp`: `auth.py` (`/api/auth`, `/api/me`), `public.py` (`/api/*`, anonymous-readable), `admin.py` (`/api/admin/*`). Register new ones in `blueprints/__init__.py`. Keep them thin; logic belongs in `features/`.
- `features/` — functional modules, no HTTP concerns: `opml.py` (import/export), `kuma.py` (Uptime Kuma sync), `weather.py` (Google Weather), `jobs.py` (scheduled jobs, `JobRun` tracking). Jobs are persisted by textual path (`app.features.jobs:<name>`): keep the path stable or let `register()` replace them.
- Dependency direction: `blueprints` → `features` → root. Root modules must not import from `features` or `blueprints` (except `create_app` wiring).

## Commands
- `task setup` install deps · `task dev` run api+web · `task test` · `task lint` · `task migrate` · `task up` docker compose

## Rules
- Visibility is enforced **server-side**: anonymous users get only `is_public` categories/links and never any status data.
- The browser never calls Google Weather or Uptime Kuma. Scheduled jobs write to the DB; the frontend reads the DB-backed endpoints.
- Secrets live in env / DB only, never in the repo. The Google Weather API key is never returned by the API (only a configured flag).
- Single user: authorization is delegated to the IdP (PocketID); any identity it authenticates for this client is admin.
- State-changing API calls require the `X-Requested-With` header and an authenticated session.
- Scheduler runs in a single gunicorn worker. `JobRun` keeps the 10 most recent runs per job.
- UI: use Nocturne tokens (`var(--color-*)`, `--space-*`, ...) and Phosphor icons only; no hard-coded colors except the status dots (`#7fbf9a` up, `#e08585` down).
- Any schema change needs a migration (`task migrate`).

## Testing
- Backend: pytest, external services (OIDC, Google, Kuma) mocked. Add tests for every visibility rule and job.
- Frontend: `npm run lint` and `npm run build` must pass.
