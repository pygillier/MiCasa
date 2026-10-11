# Single-image build: Next.js frontend + Flask API, managed by supervisord.
# The per-service Dockerfiles in backend/ and frontend/ (docker-compose.yml) are kept.

FROM node:24-slim AS web-build
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ .
# Rewrites are baked at build time: the API listens on loopback in the same container.
ENV API_URL=http://127.0.0.1:5000
RUN npm run build

FROM python:3.13-slim
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
# Node runtime for the Next.js standalone server (no npm needed).
COPY --from=web-build /usr/local/bin/node /usr/local/bin/node

# supervisord as an isolated uv tool so it does not pollute the app venv.
RUN UV_TOOL_DIR=/opt/uv-tools UV_TOOL_BIN_DIR=/usr/local/bin uv tool install supervisor

WORKDIR /app/backend
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev
COPY backend/ .

WORKDIR /app/frontend
COPY --from=web-build /app/.next/standalone ./
COPY --from=web-build /app/.next/static ./.next/static
COPY --from=web-build /app/public ./public

COPY docker/supervisord.conf /etc/supervisord.conf

ENV PATH="/app/backend/.venv/bin:$PATH" \
    DATABASE_URL=sqlite:////data/micasa.db \
    NODE_ENV=production PORT=3000 HOSTNAME=0.0.0.0 API_URL=http://127.0.0.1:5000
VOLUME /data
EXPOSE 3000
CMD ["supervisord", "-c", "/etc/supervisord.conf"]
