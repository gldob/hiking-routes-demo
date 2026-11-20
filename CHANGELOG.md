# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [1.1.0] - 2026-11-20

### Added

- `GET /api/routes/` can be filtered with `?difficulty=<T1..T6>` and `?max_distance=<km>` (inclusive). Both filters can be combined; `count` and pagination refer to the filtered result. Invalid filter values return 400.
- `GET /api/routes/` can be filtered by region with `?region=<name>`, for example `?region=Luzern`. The match is exact and case-sensitive.

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

[1.1.0]: https://github.com/gldob/hiking-routes-demo/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/gldob/hiking-routes-demo/releases/tag/v1.0.0
