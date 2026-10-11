FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY . .
ENV PATH="/app/.venv/bin:$PATH" DATABASE_URL=sqlite:////data/micasa.db
VOLUME /data
EXPOSE 5000
# One worker: the APScheduler runs in-process and must run exactly once.
CMD ["sh", "-c", "SCHEDULER_ENABLED=0 flask --app app db upgrade && exec gunicorn -w 1 --threads 4 -b 0.0.0.0:5000 'app:create_app()'"]
