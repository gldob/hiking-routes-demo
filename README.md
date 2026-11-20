# hiking-routes-demo

A small Django service to record and browse hiking routes. It serves JSON only and stores its data in SQLite.

The service is the test object for the Release Runbook Agent (HSLU DLM03 H26). Every release deliberately contains something a deployment has to take care of. See `CHANGELOG.md` for what changed and `RUNBOOK.md` for how to deploy, upgrade and roll back.

## API

| Method | Path | Description |
| --- | --- | --- |
| GET | `/health/` | Version, database status, number of pending migrations |
| GET | `/api/routes/` | List routes, 20 per page (`?page=N`); filter with `?difficulty=T2` and `?max_distance=10` (km, inclusive) |
| POST | `/api/routes/` | Create a route (token required) |
| GET | `/api/routes/<id>/` | One route |
| GET | `/api/routes/<id>/ratings/` | Ratings of a route |
| POST | `/api/routes/<id>/ratings/` | Rate a route: `{"stars": 1-5, "comment": "..."}` (token required) |

Write requests (`POST`) need the header `X-API-Token` with the value of the `API_TOKEN` environment variable; without it the API returns 401. Read requests need no token.

```bash
curl -X POST http://localhost:8000/api/routes/   -H "X-API-Token: $API_TOKEN" -H "Content-Type: application/json"   -d '{"name": "Rigi", "region": "Schwyz", "distance": 7, "elevation_gain_m": 500, "difficulty": "T2"}'
```

A route looks like this:

```json
{
  "id": 1,
  "name": "Pilatus via Fräkmüntegg",
  "region": "Luzern",
  "distance": 11.2,
  "elevation_gain_m": 1450,
  "difficulty": "T3",
  "estimated_duration_min": 375,
  "rating_average": 4.5,
  "rating_count": 2,
  "created_at": "2026-11-20T10:15:00.123456+00:00"
}
```

`distance` is in kilometres (called `distance_km` before version 2.0.0). `difficulty` uses the SAC hiking scale `T1` to `T6`. `estimated_duration_min` is the walking time after DIN 33466 (4 km/h on the flat, 300 m/h ascent; the larger partial time plus half of the smaller one, rounded to 5 minutes). `rating_average` is `null` while a route has no ratings. The list response wraps the routes:

```json
{"count": 25, "page": 1, "page_size": 20, "results": [...]}
```

Errors are JSON as well, for example `{"error": "validation_failed", "details": {"difficulty": "Must be one of T1, T2, T3, T4, T5, T6."}}` with status 400, or `{"error": "not_found"}` with status 404.

## Local development

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
export DJANGO_SECRET_KEY=dev
export API_TOKEN=dev-token
python manage.py migrate
python manage.py runserver
pytest
```

## Docker

```bash
docker build -t hiking-routes-demo .
docker run --rm -p 8000:8000 -e DJANGO_SECRET_KEY=dev -e API_TOKEN=dev-token -v hiking-data:/data hiking-routes-demo
```

The container applies migrations on start and then runs gunicorn. Released images are published to `ghcr.io/gldob/hiking-routes-demo:<tag>` by the release workflow.
