#!/bin/sh
# Without arguments: apply migrations, then start the web server.
# With arguments: run them instead, e.g. "python manage.py migrate routes 0001".
set -e

if [ "$#" -gt 0 ]; then
    exec "$@"
fi

python manage.py migrate --noinput
exec gunicorn hiking.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers "${GUNICORN_WORKERS:-2}" \
    --access-logfile -
