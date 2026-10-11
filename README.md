<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="logos/logo-dark.svg">
    <img src="logos/logo.svg" alt="MiCasa" height="80">
  </picture>

  <h1>MiCasa</h1>

  <a href="https://github.com/pygillier/MiCasa/actions/workflows/ci.yml"><img src="https://github.com/pygillier/MiCasa/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://github.com/pygillier/MiCasa/releases"><img src="https://img.shields.io/github/v/release/pygillier/MiCasa" alt="Latest release"></a>
  <a href="https://github.com/pygillier/MiCasa/pulls"><img src="https://img.shields.io/badge/PRs-welcome-ff69b4.svg" alt="PRs welcome"></a>
</div>

<details open>
<summary>Table of contents</summary>

- [About](#about)
- [Built with](#built-with)
- [Getting started](#getting-started)
- [Project structure](#project-structure)
- [Development workflow](#development-workflow)
- [Ground rules](#ground-rules)
- [Versioning and releases](#versioning-and-releases)
- [Deploy](#deploy)
- [Contributing](#contributing)
- [Acknowledgements](#acknowledgements)

</details>

## About

MiCasa is a personal startpage meant to be self-hosted behind a reverse proxy.

- **Anonymous** visitors see only categories and links marked *public*, never any status data.
- **Logged in** (PocketID): everything, with Uptime Kuma dots; `/admin` manages categories, links and settings.
- **Weather**: Google Weather API, fetched by an APScheduler job (hourly by default) and cached in SQLite. The browser only reads `/api/weather`.
- **Uptime Kuma**: monitors synced every 60 s by a scheduler job via [uptime-kuma-api2](https://github.com/pbarone/uptime-kuma-api2); pick a monitor per link in admin.
- The last 10 runs of each job are kept (Admin → Settings).

## Built with

| Part | Tech |
|---|---|
| `frontend/` | Next.js (App Router, TypeScript), proxies `/api/*` to Flask on the same origin |
| `backend/` | Flask, Flask-SQLAlchemy, Flask-Migrate, Authlib (OIDC + PKCE), Flask-APScheduler |
| Storage | SQLite |
| Tooling | [mise](https://mise.jdx.dev) (versions), [Task](https://taskfile.dev) (commands), [uv](https://docs.astral.sh/uv/) (Python), pre-commit |

## Getting started

### Prerequisites

Install [mise](https://mise.jdx.dev/getting-started.html); it provides Python 3.13, Node 24, uv, task and pre-commit (see [`mise.toml`](mise.toml)).
You need a PocketID (or any OIDC provider) client to log in; weather and Uptime Kuma are optional.

### Installation

```bash
git clone git@github.com:pygillier/MiCasa.git && cd MiCasa
mise install          # python, node, uv, task, pre-commit
task setup            # uv sync + npm install
cp .env.example .env  # then fill it in (export it, or use direnv)
task migrate          # create/upgrade the SQLite database
task dev              # api on :5000, web on :3000 (proxies /api)
```

Open <http://localhost:3000>. Run `task --list` for every available command.

### Configuration

Secrets live in the environment or the database, never in the repository.

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Flask session signing key (long random string) |
| `PUBLIC_URL` | Public base URL; the OIDC redirect URI is `${PUBLIC_URL}/api/auth/callback` |
| `OIDC_ISSUER`, `OIDC_CLIENT_ID`, `OIDC_CLIENT_SECRET` | PocketID client (authorization code + PKCE) |
| `GOOGLE_WEATHER_API_KEY` | Weather API key; can also be set from Admin → Settings |
| `KUMA_URL`, `KUMA_USERNAME`, `KUMA_PASSWORD` | Uptime Kuma socket.io login (UI API keys do not work) |
| `LOG_LEVEL`, `LOG_JSON` | Logging verbosity and JSON output |

## Project structure

```text
backend/app/
├── __init__.py, config.py, extensions.py, logs.py, models.py,
│   settings.py, auth.py, validation.py     # technical plumbing only
├── blueprints/   # HTTP layer: auth.py, public.py, admin.py (thin)
└── features/     # functional code, no HTTP: opml, kuma, weather, jobs
frontend/
├── app/          # routes (page.tsx, admin/), nocturne.css, themes.css
├── components/   # UI; components/admin/ holds the admin tabs
└── lib/          # api client, i18n messages, themes, types
```

Dependency direction is `blueprints` → `features` → root. Root modules must not import from `features` or `blueprints` (except the `create_app` wiring).
Scheduled jobs are persisted by textual path (`app.features.jobs:<name>`): keep the path stable or let `register()` replace them.

## Development workflow

| Command | What it does |
|---|---|
| `task dev` | Run API and web in parallel |
| `task test` | Backend tests (pytest) |
| `task lint` | `ruff check` (backend) and `npm run lint` (frontend) |
| `task build` | Production build of the frontend |
| `task migration -- "message"` | Generate a migration after a schema change |
| `task migrate` | Apply migrations |

Before opening a pull request:

- `task test` and `task lint` pass, and `npm run build` succeeds in `frontend/`.
- Any schema change comes with a migration (`task migration -- "..."`).
- Backend tests mock external services (OIDC, Google, Kuma). Add tests for every visibility rule and every job.
- Install the hooks once with `pre-commit install` (and `pre-commit install --hook-type pre-push` to run pytest on push).

## Ground rules

These are enforced in review; please keep them in mind when contributing.

- Visibility is enforced **server-side**: anonymous users get only public categories/links and never status data.
- The browser never calls Google Weather or Uptime Kuma. Scheduled jobs write to the DB; the frontend reads DB-backed endpoints.
- The Google Weather API key is never returned by the API (only a configured flag).
- State-changing API calls require the `X-Requested-With` header and an authenticated session.
- Single user: authorization is delegated to the IdP; any identity it authenticates for this client is admin.
- The scheduler runs in a single gunicorn worker.
- **UI**: use Nocturne tokens (`var(--color-*)`, `--space-*`, …) and Phosphor icons only. No hard-coded colors except the status dots (`#7fbf9a` up, `#e08585` down).
- **UI sizing**: lengths are in `rem`, never `px`, except hairlines (borders, outlines, shadows), radii and gradient ramps. The whole UI scales from `html { font-size }` in `frontend/app/nocturne.css`. Inline styles in TSX use `rem` too.

## Versioning and releases

[Semantic Versioning](https://semver.org); git tags `vX.Y.Z` are the source of truth.

```bash
task version                    # current version
task release -- patch           # or minor | major | X.Y.Z (add --dry-run to preview)
git push --follow-tags
```

`release` requires a clean tree, bumps `backend/pyproject.toml` and `frontend/package.json`, commits and tags.
Pushing a `vX.Y.Z` tag that is on `main` triggers the [release workflow](.github/workflows/release.yml): it waits for CI to pass on that commit, pushes the images to GHCR and creates the GitHub release.

## Deploy

```bash
cp .env.example .env   # fill in
task up                # docker compose (api + web); data in ./data
```

### Single image

The root `Dockerfile` bundles the frontend and the API in one image, run by supervisord (web on port 3000, API on loopback):

```bash
task up:single         # or: docker compose -f docker-compose.single.yml up -d --build
task docker:build      # build all images (api, web, single)
```

Both variants use `./data` for the SQLite database.

Register an OIDC client in PocketID with redirect URI `${PUBLIC_URL}/api/auth/callback` (authorization code + PKCE).
Put a TLS reverse proxy in front of the `web` service (port 3000; the `micasa` container in single-image mode) and set `PUBLIC_URL` to the https URL.

## Contributing

1. Open an issue (or comment on an existing one) before starting larger changes.
2. Branch from `main`, keep changes focused, and follow the [ground rules](#ground-rules).
3. Run `task test && task lint` and make sure the frontend builds.
4. Open a pull request describing what changed and why.

## Acknowledgements

- [PocketID](https://github.com/pocket-id/pocket-id) for OIDC
- [Uptime Kuma](https://github.com/louislam/uptime-kuma) and [uptime-kuma-api2](https://github.com/pbarone/uptime-kuma-api2)
- [Phosphor Icons](https://phosphoricons.com)
- README structure inspired by [amazing-github-template](https://github.com/dec0dOS/amazing-github-template)
