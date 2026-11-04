#!/bin/sh
set -e

# create or update tables (db is already healthy thanks to depends_on)
python manage.py migrate --noinput

# copy admin and swagger static files to the volume shared with nginx
python manage.py collectstatic --noinput

# daphne is an ASGI server, so websockets will work on it later
exec daphne -b 0.0.0.0 -p 8000 config.asgi:application
