FROM python:3.13.11-slim
RUN apt-get update && apt-get install -y libpq-dev gcc

WORKDIR /app

RUN python -m pip install uv
COPY pyproject.toml .
RUN python -m uv sync

COPY notification_service notification_service/
COPY .env .

WORKDIR /app/notification_service
ENV PATH="/app/.venv/bin:$PATH"
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
RUN python manage.py collectstatic --noinput
ENTRYPOINT ["/entrypoint.sh"]
