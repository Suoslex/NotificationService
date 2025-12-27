FROM python:3.13.11-alpine

WORKDIR /app

RUN python -m pip install uv
COPY pyproject.toml .
RUN python -m uv sync

COPY notification_service notification_service/
COPY .env .

WORKDIR /app/notification_service
ENV PATH="/app/.venv/bin:$PATH"
CMD ["gunicorn", "notification_service.config.wsgi", "--bind", "0.0.0.0:8000"]
