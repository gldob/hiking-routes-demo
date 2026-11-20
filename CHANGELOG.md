# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [1.2.0] - 2026-11-20

### Added

- Ratings: `POST /api/routes/<id>/ratings/` with `{"stars": 1-5, "comment": "..."}` rates a route (201); `GET /api/routes/<id>/ratings/` lists its ratings. Invalid `stars` return 400, unknown routes 404.
- Routes include `rating_average` (one decimal, `null` without ratings) and `rating_count`.
- Routes include `estimated_duration_min`, the walking time after DIN 33466 (4 km/h, 300 m ascent/h, larger time plus half of the smaller, rounded to 5 minutes). Example: 12 km and 600 m give 240.

### Database

- New migration `routes.0002_rating` creates the table `routes_rating`. It runs on container start. Rolling back to v1.1.0 requires reverting it first (see RUNBOOK), which deletes all ratings.

## [1.1.0] - 2026-11-20

### Added

- `GET /api/routes/` can be filtered with `?difficulty=<T1..T6>` and `?max_distance=<km>` (inclusive). Both filters can be combined; `count` and pagination refer to the filtered result. Invalid filter values return 400.

### Fixed

- Creating a route with a negative `distance_km` now returns 400 instead of 201. Existing routes are not changed.

## [1.0.0] - 2026-11-20

First release.

### Added

- Record hiking routes with name, region, distance in km (`distance_km`), elevation gain in m (`elevation_gain_m`) and difficulty on the SAC scale `T1`–`T6`.
- `POST /api/routes/` creates a route and returns it with status 201. Invalid input returns 400 with field-level details.
- `GET /api/routes/` lists routes ordered by creation, 20 per page; select a page with `?page=N`.
- `GET /api/routes/<id>/` returns one route, or 404.
- `GET /health/` reports the running version, the database status and the number of pending migrations.
- Docker image with gunicorn; migrations are applied on container start. Images are published to GHCR per tag.

[1.2.0]: https://github.com/gldob/hiking-routes-demo/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/gldob/hiking-routes-demo/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/gldob/hiking-routes-demo/releases/tag/v1.0.0
