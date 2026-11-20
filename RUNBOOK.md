# Runbook: hiking-routes-demo v1.1.0

How to deploy, upgrade, check and roll back the service. All commands assume a Linux host with Docker and a POSIX shell.

## 1. Prerequisites

- Docker 24 or newer
- Port 8000 free on the host
- Pull access to `ghcr.io/gldob/hiking-routes-demo`

Set these shell variables once; all later commands use them:

```bash
export IMAGE=ghcr.io/gldob/hiking-routes-demo
export VERSION=v1.1.0
export PREVIOUS=v1.0.0
export CONTAINER=hiking-routes
export VOLUME=hiking-data
export DJANGO_SECRET_KEY="<the value used for the running deployment>"
```

For a fresh install, generate a new key with `openssl rand -hex 32` and keep it.

## 2. Configuration

| Variable | Required | Default | Purpose |
| --- | --- | --- | --- |
| `DJANGO_SECRET_KEY` | yes | – | Django secret key. Without it the container exits on start with `ImproperlyConfigured`. |
| `DJANGO_ALLOWED_HOSTS` | no | `*` | Comma-separated host names the service answers to. |
| `DJANGO_DEBUG` | no | `0` | `1` enables Django debug mode. Never in production. |
| `PORT` | no | `8000` | Port gunicorn listens on inside the container. |
| `GUNICORN_WORKERS` | no | `2` | Number of gunicorn worker processes. |
| `DATABASE_PATH` | no | `/data/db.sqlite3` | Location of the SQLite file. Keep it inside the volume. |

No configuration changes compared to v1.0.0.

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

On start the container runs `python manage.py migrate`, then starts gunicorn.

## 4. Health check

```bash
curl -fsS http://localhost:8000/health/
```

Expected answer (status 200):

```json
{"status": "ok", "version": "1.1.0", "database": "ok", "pending_migrations": 0}
```

If the call fails, read the logs with `docker logs "$CONTAINER"`.

Smoke test for this release:

```bash
curl -fsS "http://localhost:8000/api/routes/?difficulty=T1&max_distance=10"
curl -s -o /dev/null -w '%{http_code}\n' -X POST http://localhost:8000/api/routes/ \
  -H 'Content-Type: application/json' \
  -d '{"name": "Smoke test", "region": "Test", "distance_km": -1, "elevation_gain_m": 0, "difficulty": "T1"}'
```

The first call returns 200 with only T1 routes of at most 10 km. The second prints `400`.

## 5. Upgrade from v1.0.0

This release has no database migration and no new configuration. The upgrade is an image swap.

1. Back up the database (section 6).
2. Pull the new image:
   ```bash
   docker pull "$IMAGE:$VERSION"
   ```
3. Replace the container, keeping volume and variables:
   ```bash
   docker stop "$CONTAINER" && docker rm "$CONTAINER"
   docker run -d --name "$CONTAINER" \
     -p 8000:8000 \
     -v "$VOLUME":/data \
     -e DJANGO_SECRET_KEY="$DJANGO_SECRET_KEY" \
     --restart unless-stopped \
     "$IMAGE:$VERSION"
   ```
4. Run the health check (section 4); `version` must be `1.1.0`.

Behaviour change to tell API clients: a negative `distance_km` is now rejected with 400.

## 6. Backup

Before any change, copy the database file inside the volume:

```bash
docker exec "$CONTAINER" cp /data/db.sqlite3 "/data/db.sqlite3.bak-$(date +%Y%m%d%H%M%S)"
```

## 7. Rollback to v1.0.0

No migration to revert. Swap the image back:

```bash
docker stop "$CONTAINER" && docker rm "$CONTAINER"
docker run -d --name "$CONTAINER" \
  -p 8000:8000 \
  -v "$VOLUME":/data \
  -e DJANGO_SECRET_KEY="$DJANGO_SECRET_KEY" \
  --restart unless-stopped \
  "$IMAGE:$PREVIOUS"
curl -fsS http://localhost:8000/health/
```

`version` must be `1.0.0`. All routes created with v1.1.0 remain available.
