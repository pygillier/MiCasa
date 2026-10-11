# MiCasa v2

Single-user startpage: categories of links, Uptime Kuma status dots, weather, and an OIDC-protected admin.
Next.js frontend · Flask API · SQLite. Design reference: `mockups/Startpage.dc.html`.

## Behaviour
- **Anonymous**: only categories and links marked *public*, no status dots.
- **Logged in (PocketID)**: everything, with Uptime Kuma dots; `/admin` to manage categories, links and settings.
- **Weather**: Google Weather API, fetched by an APScheduler job (hourly by default) and cached in SQLite; the browser only reads `/api/weather`.
- **Uptime Kuma**: monitors synced every 60 s by a scheduler job via [uptime-kuma-api2](https://github.com/pbarone/uptime-kuma-api2); pick a monitor per link in admin.
- The last 10 runs of each job are kept (Admin → Settings).

## Develop
```bash
mise install          # python, node, uv, task
task setup
cp .env.example .env  # and export it (or use direnv)
task migrate
task dev              # api :5000, web :3000 (proxies /api)
task test && task lint
```

## Deploy
```bash
cp .env.example .env   # fill in
task up                # docker compose; data in ./data
```
Register an OIDC client in PocketID with redirect URI `${PUBLIC_URL}/api/auth/callback` (authorization code + PKCE).
Put a TLS reverse proxy in front of the `web` service (port 3000) and set `PUBLIC_URL` to the https URL.
