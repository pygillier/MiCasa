FROM python:3.12-slim AS python-base
ARG BRANCH="main"
ARG COMMIT=""
ARG VERSION="develop"
LABEL authors="Pierre-Yves Gillier <github@pygillier.me>"
LABEL branch=${BRANCH}
LABEL commit=${COMMIT}
LABEL version=${VERSION}

ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    # poetry
    # https://python-poetry.org/docs/configuration/#using-environment-variables
    POETRY_VERSION=1.8.4 \
    # make poetry install to this location
    POETRY_HOME="/opt/poetry" \
    # make poetry create the virtual environment in the project's root
    # it gets named `.venv`
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1 \
    \
    # paths
    # this is where our requirements + virtual environment will live
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

FROM python-base AS builder-base
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        # deps for installing poetry
        curl \
        # deps for building python deps
        build-essential \
        # I18N for gjango \
        gettext \
        libgettextpo-dev \
    # install poetry - respects $POETRY_VERSION & $POETRY_HOME
    && curl -sSL https://install.python-poetry.org | python3 -

# copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH
COPY . ./

# install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
RUN poetry install --without dev && SECRET_KEY=dumb python manage.py compilemessages --ignore=.venv


# NodeJS for tailwind css
FROM node:20 AS node-builder
WORKDIR /node
COPY . /node/
RUN npm install --no-fund && npx tailwindcss -i static/css/input.css -o production.css --minify

# Production image
FROM python-base AS production

WORKDIR /app
# Copy all elements
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH
COPY . /app/
COPY --from=builder-base $PYSETUP_PATH/locale/ $PYSETUP_PATH/locale/
COPY --from=node-builder /node/production.css /app/static/css/output.css

RUN SECRET_KEY=static python manage.py collectstatic



# Image identifiers
ENV COMMIT_SHA=${COMMIT}
ENV COMMIT_BRANCH=${BRANCH}
ENV VERSION=${VERSION}

RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
