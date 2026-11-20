from hiking import __version__


def test_health_reports_version_and_database(client, db):
    response = client.get("/health/")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "version": __version__,
        "database": "ok",
        "pending_migrations": 0,
    }


def test_unknown_url_returns_json_404(client, db):
    response = client.get("/does-not-exist/")

    assert response.status_code == 404
    assert response.json() == {"error": "not_found"}
