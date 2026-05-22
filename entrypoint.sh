#!/bin/sh


python manage.py migrate --no-input
#python manage.py collectstatic --noinput
exec gunicorn --bind 0.0.0.0:8080 biblioteca.wsgi:application --workers 4 --timeout 60