#!/usr/bin/env sh

cd /app || exit
mkdir /data
python manage.py migrate

gunicorn -b 0.0.0.0:8000 MiCasa.wsgi
