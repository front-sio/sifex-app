FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# system deps (psycopg)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# collectstatic at build time is OK only if settings don't require DB.
# If your collectstatic needs env vars, do it at runtime (see start.sh).
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000
CMD ["gunicorn", "sifex.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]
