# Runbook: hiking-routes-demo v1.0.0

How to deploy, check and remove the service. All commands assume a Linux host with Docker and a POSIX shell.

## 1. Prerequisites

- Docker 24 or newer
- Port 8000 free on the host
- Pull access to `ghcr.io/gldob/hiking-routes-demo`

Set these shell variables once; all later commands use them:

```bash
export IMAGE=ghcr.io/gldob/hiking-routes-demo
export VERSION=v1.0.0
export CONTAINER=hiking-routes
export VOLUME=hiking-data
export DJANGO_SECRET_KEY="$(openssl rand -hex 32)"   # keep this value, reuse it for every later deployment
```

## 2. Configuration

| Variable | Required | Default | Purpose |
| --- | --- | --- | --- |
| `DJANGO_SECRET_KEY` | yes | – | Django secret key. Without it the container exits on start with `ImproperlyConfigured`. |
| `DJANGO_ALLOWED_HOSTS` | no | `*` | Comma-separated host names the service answers to. |
| `DJANGO_DEBUG` | no | `0` | `1` enables Django debug mode. Never in production. |
| `PORT` | no | `8000` | Port gunicorn listens on inside the container. |
| `GUNICORN_WORKERS` | no | `2` | Number of gunicorn worker processes. |
| `DATABASE_PATH` | no | `/data/db.sqlite3` | Location of the SQLite file. Keep it inside the volume. |

Data lives in the SQLite file in the Docker volume mounted at `/data`. Losing the volume loses all routes.

## 3. Deploy (fresh install)

```bash
docker pull "$IMAGE:$VERSION"
docker volume create "$VOLUME"
docker run -d --name "$CONTAINER" \
  -p 8000:8000 \
  -v "$VOLUME":/data \
  -e DJANGO_SECRET_KEY="$DJANGO_SECRET_KEY" \
  --restart unless-stopped \
  "$IMAGE:$VERSION"
```

On start the container runs `python manage.py migrate` and creates the table `routes_route` (migration `routes.0001_initial`), then starts gunicorn.

## 4. Health check

```bash
curl -fsS http://localhost:8000/health/
```

Expected answer (status 200):

```json
{"status": "ok", "version": "1.0.0", "database": "ok", "pending_migrations": 0}
```

If the call fails, read the logs with `docker logs "$CONTAINER"`.

Smoke test:

```bash
curl -fsS -X POST http://localhost:8000/api/routes/ \
  -H 'Content-Type: application/json' \
  -d '{"name": "Smoke test", "region": "Test", "distance_km": 5, "elevation_gain_m": 200, "difficulty": "T1"}'
curl -fsS http://localhost:8000/api/routes/
```

The POST returns 201, the list contains the new route.

## 5. Upgrade

Not applicable: v1.0.0 is the first release.

## 6. Backup

Before any change, copy the database file inside the volume:

```bash
docker exec "$CONTAINER" cp /data/db.sqlite3 "/data/db.sqlite3.bak-$VERSION"
```

## 7. Rollback / removal

There is no earlier version to roll back to. To remove the service and keep the data:

```bash
docker stop "$CONTAINER" && docker rm "$CONTAINER"
```

To also delete all data: `docker volume rm "$VOLUME"`.
