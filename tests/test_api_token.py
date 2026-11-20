import pytest
from django.core.exceptions import ImproperlyConfigured
from django.test import Client

ROUTE = {"name": "Rigi", "region": "Schwyz", "distance_km": 7, "elevation_gain_m": 500, "difficulty": "T2"}


@pytest.mark.django_db
def test_create_without_token_returns_401(anonymous_client):
    response = anonymous_client.post("/api/routes/", ROUTE, content_type="application/json")

    assert response.status_code == 401
    assert response.json()["error"] == "unauthorized"


@pytest.mark.django_db
def test_create_with_wrong_token_returns_401():
    client = Client(headers={"X-API-Token": "wrong"})

    response = client.post("/api/routes/", ROUTE, content_type="application/json")

    assert response.status_code == 401


@pytest.mark.django_db
def test_create_with_token_returns_201(client):
    response = client.post("/api/routes/", ROUTE, content_type="application/json")

    assert response.status_code == 201


def test_rating_without_token_returns_401(anonymous_client, make_route):
    route = make_route()

    response = anonymous_client.post(
        f"/api/routes/{route.id}/ratings/", {"stars": 5}, content_type="application/json"
    )

    assert response.status_code == 401


def test_reading_needs_no_token(anonymous_client, make_route):
    route = make_route()

    assert anonymous_client.get("/api/routes/").status_code == 200
    assert anonymous_client.get(f"/api/routes/{route.id}/").status_code == 200
    assert anonymous_client.get(f"/api/routes/{route.id}/ratings/").status_code == 200
    assert anonymous_client.get("/health/").status_code == 200


def test_settings_refuse_to_load_without_api_token(monkeypatch):
    import importlib

    import hiking.settings

    monkeypatch.delenv("API_TOKEN")
    with pytest.raises(ImproperlyConfigured, match="API_TOKEN"):
        importlib.reload(hiking.settings)
