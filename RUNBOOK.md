# Runbook: hiking-routes-demo v1.2.0

How to deploy, upgrade, check and roll back the service. All commands assume a Linux host with Docker and a POSIX shell.

## 1. Prerequisites

- Docker 24 or newer
- Port 8000 free on the host
- Pull access to `ghcr.io/gldob/hiking-routes-demo`

Set these shell variables once; all later commands use them:

```bash
export IMAGE=ghcr.io/gldob/hiking-routes-demo
export VERSION=v1.2.0
export PREVIOUS=v1.1.0
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

No configuration changes compared to v1.1.0.

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

On start the container runs `python manage.py migrate` (migrations `routes.0001_initial` and `routes.0002_rating`), then starts gunicorn.

## 4. Health check

```bash
curl -fsS http://localhost:8000/health/
```

Expected answer (status 200):

```json
{"status": "ok", "version": "1.2.0", "database": "ok", "pending_migrations": 0}
```

If the call fails, read the logs with `docker logs "$CONTAINER"`.

Smoke test for this release (replace `1` with the id of an existing route):

```bash
curl -fsS -X POST http://localhost:8000/api/routes/1/ratings/ \
  -H 'Content-Type: application/json' -d '{"stars": 5}'
curl -fsS http://localhost:8000/api/routes/1/
```

The POST returns 201. The route shows `rating_count` of at least 1, a `rating_average` and `estimated_duration_min`.

## 5. Upgrade from v1.1.0

This release contains a **database migration**: `routes.0002_rating` creates the new table `routes_rating`. Existing tables are not changed. The migration runs automatically on container start.

1. Back up the database (section 6). Do not skip this step.
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
4. Check that the migration was applied:
   ```bash
   docker logs "$CONTAINER" 2>&1 | grep "Applying routes.0002_rating"
   docker exec "$CONTAINER" python manage.py showmigrations routes
   ```
   Both `0001_initial` and `0002_rating` are marked `[X]`.
5. Run the health check (section 4); `version` must be `1.2.0` and `pending_migrations` must be `0`.

## 6. Backup

Before any change, copy the database file inside the volume:

```bash
docker exec "$CONTAINER" cp /data/db.sqlite3 "/data/db.sqlite3.bak-$(date +%Y%m%d%H%M%S)"
```

## 7. Rollback to v1.1.0

The migration has to be reverted **before** the image is switched, and it has to be reverted **with the v1.2.0 image**: the v1.1.0 image does not know migration `0002_rating` and cannot undo it.

Reverting drops the table `routes_rating`, so **all ratings are lost**. Routes are kept unchanged.

1. Back up the database (section 6).
2. Stop the running container:
   ```bash
   docker stop "$CONTAINER" && docker rm "$CONTAINER"
   ```
3. Revert the migration with the current image:
   ```bash
   docker run --rm \
     -v "$VOLUME":/data \
     -e DJANGO_SECRET_KEY="$DJANGO_SECRET_KEY" \
     "$IMAGE:$VERSION" \
     python manage.py migrate routes 0001
   ```
   The output ends with `Unapplying routes.0002_rating... OK`.
4. Start the previous version:
   ```bash
   docker run -d --name "$CONTAINER" \
     -p 8000:8000 \
     -v "$VOLUME":/data \
     -e DJANGO_SECRET_KEY="$DJANGO_SECRET_KEY" \
     --restart unless-stopped \
     "$IMAGE:$PREVIOUS"
   ```
5. Run the health check; `version` must be `1.1.0`. `GET /api/routes/` returns all routes that existed before the rollback, without rating fields.
