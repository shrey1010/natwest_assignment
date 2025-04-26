#!/bin/bash

echo "Starting up the container..."

echo "Applying migrations..."
python manage.py makemigrations users
python manage.py makemigrations app
python manage.py makemigrations django_celery_beat
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting server..."
exec python manage.py runserver 0.0.0.0:8000
