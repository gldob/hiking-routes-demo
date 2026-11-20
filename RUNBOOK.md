# Runbook: hiking-routes-demo v2.0.0

How to deploy, upgrade, check and roll back the service. All commands assume a Linux host with Docker and a POSIX shell.

**v2.0.0 is a major release.** It contains a database migration and changes the API for clients. Read section 5 before upgrading.

## 1. Prerequisites

- Docker 24 or newer
- Port 8000 free on the host
- Pull access to `ghcr.io/gldob/hiking-routes-demo`

Set these shell variables once; all later commands use them:

```bash
export IMAGE=ghcr.io/gldob/hiking-routes-demo
export VERSION=v2.0.0
export PREVIOUS=v1.2.0
export CONTAINER=hiking-routes
export VOLUME=hiking-data
export DJANGO_SECRET_KEY="<the value used for the running deployment>"
```

For a fresh install, also generate a new `DJANGO_SECRET_KEY` with `openssl rand -hex 32` and keep it.

## 2. Configuration

| Variable | Required | Default | Purpose |
| --- | --- | --- | --- |
| `DJANGO_SECRET_KEY` | yes | – | Django secret key. Without it the container exits on start with `ImproperlyConfigured`. |
| `DJANGO_ALLOWED_HOSTS` | no | `*` | Comma-separated host names the service answers to. |
| `DJANGO_DEBUG` | no | `0` | `1` enables Django debug mode. Never in production. |
| `PORT` | no | `8000` | Port gunicorn listens on inside the container. |
| `GUNICORN_WORKERS` | no | `2` | Number of gunicorn worker processes. |
| `DATABASE_PATH` | no | `/data/db.sqlite3` | Location of the SQLite file. Keep it inside the volume. |

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

On start the container runs `python manage.py migrate` (migrations `routes.0001` to `routes.0003`), then starts gunicorn.

## 4. Health check

```bash
curl -fsS http://localhost:8000/health/
```

Expected answer (status 200):

```json
{"status": "ok", "version": "2.0.0", "database": "ok", "pending_migrations": 0}
```

If the call fails, read the logs with `docker logs "$CONTAINER"`.

Smoke test for this release:

```bash
# without token: 401
curl -s -o /dev/null -w '%{http_code}\n' -X POST http://localhost:8000/api/routes/ \
  -H 'Content-Type: application/json' \
  -d '{"name": "Smoke test", "region": "Test", "distance": 5, "elevation_gain_m": 200, "difficulty": "T1"}'
# with token: 201, the response contains "distance" and no "distance_km"
curl -fsS -X POST http://localhost:8000/api/routes/ \
  -H "X-API-Token: <token>" -H 'Content-Type: application/json' \
  -d '{"name": "Smoke test", "region": "Test", "distance": 5, "elevation_gain_m": 200, "difficulty": "T1"}'
```

## 5. Upgrade from v1.2.0

What changes for operations:

- **Database migration** `routes.0003_rename_distance_km_route_distance` renames the column `routes_route.distance_km` to `distance`. It runs automatically on container start. Values are kept.

What changes for API clients (announce before the upgrade):

- `POST` requests need the header `X-API-Token`, otherwise 401.
- The field `distance_km` is now `distance` in requests and responses.

Steps:

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
   docker logs "$CONTAINER" 2>&1 | grep "Applying routes.0003_rename_distance_km_route_distance"
   docker exec "$CONTAINER" python manage.py showmigrations routes
   ```
   `0001_initial`, `0002_rating` and `0003_rename_distance_km_route_distance` are marked `[X]`.
5. Run the health check and the smoke test (section 4); `version` must be `2.0.0`.

## 6. Backup

Before any change, copy the database file inside the volume:

```bash
docker exec "$CONTAINER" cp /data/db.sqlite3 "/data/db.sqlite3.bak-$(date +%Y%m%d%H%M%S)"
```

## 7. Rollback to v1.2.0

The migration has to be reverted **before** the image is switched, and it has to be reverted **with the v2.0.0 image**: the v1.2.0 image does not know migration `0003` and would fail with 500 on every route request because the column is named `distance`.

Reverting renames the column back to `distance_km`. No data is lost; routes and ratings are kept.

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
     python manage.py migrate routes 0002
   ```
   The output ends with `Unapplying routes.0003_rename_distance_km_route_distance... OK`.
4. Start the previous version:
   ```bash
   docker run -d --name "$CONTAINER" \
     -p 8000:8000 \
     -v "$VOLUME":/data \
     -e DJANGO_SECRET_KEY="$DJANGO_SECRET_KEY" \
     --restart unless-stopped \
     "$IMAGE:$PREVIOUS"
   ```
5. Run the health check; `version` must be `1.2.0`. Routes show `distance_km` again, and `POST` works without a token.
