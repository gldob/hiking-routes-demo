FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATABASE_PATH=/data/db.sqlite3 \
    PORT=8000

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x docker-entrypoint.sh \
    && useradd --system --uid 1000 app \
    && mkdir -p /data \
    && chown app /data

USER app
VOLUME ["/data"]
EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint.sh"]
