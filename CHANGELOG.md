# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [1.0.0] - 2026-11-20

First release.

### Added

- Record hiking routes with name, region, distance in km (`distance_km`), elevation gain in m (`elevation_gain_m`) and difficulty on the SAC scale `T1`–`T6`.
- `POST /api/routes/` creates a route and returns it with status 201. Invalid input returns 400 with field-level details.
- `GET /api/routes/` lists routes ordered by creation, 20 per page; select a page with `?page=N`.
- `GET /api/routes/<id>/` returns one route, or 404.
- `GET /health/` reports the running version, the database status and the number of pending migrations.
- Docker image with gunicorn; migrations are applied on container start. Images are published to GHCR per tag.

[1.0.0]: https://github.com/gldob/hiking-routes-demo/releases/tag/v1.0.0
