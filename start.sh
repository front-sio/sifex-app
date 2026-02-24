#!/usr/bin/env bash
set -e

max_retries="${DB_MAX_RETRIES:-30}"
sleep_seconds="${DB_RETRY_SECONDS:-2}"
db_ready=0

echo "Waiting for database..."
for i in $(seq 1 "$max_retries"); do
  if python - <<'PY'
import os
import sys
import traceback

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sifex.settings")

try:
    import django
    django.setup()
    from django.db import connections
    connections["default"].cursor()
except Exception as exc:
    print(f"Database check failed: {exc.__class__.__name__}: {exc}", file=sys.stderr)
    traceback.print_exc(limit=1)
    sys.exit(1)
PY
  then
    db_ready=1
    break
  fi
  echo "Database not ready, retrying ($i/$max_retries)..."
  sleep "$sleep_seconds"
done

if [ "$db_ready" -ne 1 ]; then
  echo "Database not ready after $max_retries attempts"
  exit 1
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput
exec gunicorn sifex.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
