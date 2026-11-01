# Pinned to 3.12 rather than the 3.14 on the author's machine: 3.14 is new enough
# that several binary wheels (asyncpg among them) are not reliably published yet,
# and a container that builds anywhere is worth more than matching the host.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /srv

# Dependencies first so the layer caches across source edits.
COPY pyproject.toml README.md ./
COPY app ./app
RUN pip install -e ".[anthropic,openai]"

COPY alembic.ini ./
COPY infra ./infra
COPY evals ./evals
COPY ui ./ui

# Run as a non-root user.
RUN useradd --create-home --uid 10001 appuser && chown -R appuser:appuser /srv
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
