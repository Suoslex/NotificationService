#!/bin/sh
set -e

python manage.py migrate

gunicorn notification_service.config.wsgi --bind 0.0.0.0:8000