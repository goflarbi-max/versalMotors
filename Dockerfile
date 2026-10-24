# syntax=docker/dockerfile:1.7

FROM python:3.12-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/install/lib/python3.12/site-packages

WORKDIR /app

COPY backend/requirements.lock /tmp/backend-requirements.lock
RUN python -m pip install --prefix=/install -r /tmp/backend-requirements.lock

COPY config ./config
COPY data/raw ./data/raw
COPY docs/cleaning_log.csv ./docs/cleaning_log.csv
COPY scripts ./scripts
COPY src ./src
COPY tests/parity_baseline.json ./tests/parity_baseline.json
COPY deployment/verify_database.py ./deployment/verify_database.py

RUN python scripts/build_database.py \
    && python deployment/verify_database.py \
        --database data/business.duckdb \
        --baseline tests/parity_baseline.json


FROM python:3.12-slim AS runtime

ENV HOME=/home/versalmotors \
    PATH=/home/versalmotors/.local/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VERSALMOTORS_DB_PATH=/app/data/business.duckdb

RUN groupadd --gid 10001 versalmotors \
    && useradd --uid 10001 --gid versalmotors --create-home versalmotors

WORKDIR /app

COPY --from=builder /install /usr/local
COPY --chown=versalmotors:versalmotors backend ./backend
COPY --chown=versalmotors:versalmotors src ./src
COPY --from=builder --chown=versalmotors:versalmotors /app/data/business.duckdb ./data/business.duckdb
COPY --from=builder --chown=versalmotors:versalmotors /app/docs/cleaning_log.csv ./docs/cleaning_log.csv

USER 10001:10001

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.getenv('PORT', '8000') + '/health/ready', timeout=4)"

CMD ["sh", "-c", "exec uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --proxy-headers --forwarded-allow-ips='*'"]
