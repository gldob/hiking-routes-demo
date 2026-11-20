import pytest

VALID_ROUTE = {
    "name": "Pilatus via Fräkmüntegg",
    "region": "Luzern",
    "distance": 11.2,
    "elevation_gain_m": 1450,
    "difficulty": "T3",
}


@pytest.mark.django_db
def test_create_route_returns_201_and_the_route(client):
    response = client.post("/api/routes/", VALID_ROUTE, content_type="application/json")

    assert response.status_code == 201
    body = response.json()
    assert body["id"] > 0
    assert {key: body[key] for key in VALID_ROUTE} == VALID_ROUTE


@pytest.mark.django_db
def test_created_route_can_be_fetched(client):
    created = client.post("/api/routes/", VALID_ROUTE, content_type="application/json").json()

    response = client.get(f"/api/routes/{created['id']}/")

    assert response.status_code == 200
    assert response.json() == created


@pytest.mark.django_db
def test_unknown_route_returns_404(client):
    response = client.get("/api/routes/999/")

    assert response.status_code == 404
    assert response.json() == {"error": "not_found"}


@pytest.mark.django_db
@pytest.mark.parametrize(
    "field, value",
    [
        ("name", ""),
        ("region", None),
        ("distance", "far"),
        ("distance", -3.5),
        ("elevation_gain_m", -10),
        ("difficulty", "T7"),
    ],
)
def test_invalid_route_is_rejected(client, field, value):
    payload = {**VALID_ROUTE, field: value}

    response = client.post("/api/routes/", payload, content_type="application/json")

    assert response.status_code == 400
    assert field in response.json()["details"]


@pytest.mark.django_db
def test_old_field_name_distance_km_is_rejected(client):
    payload = {key: value for key, value in VALID_ROUTE.items() if key != "distance"}
    payload["distance_km"] = 11.2

    response = client.post("/api/routes/", payload, content_type="application/json")

    assert response.status_code == 400
    assert set(response.json()["details"]) == {"distance", "distance_km"}


@pytest.mark.django_db
def test_route_has_no_distance_km_field(client):
    body = client.post("/api/routes/", VALID_ROUTE, content_type="application/json").json()

    assert "distance_km" not in body
    assert body["distance"] == 11.2


@pytest.mark.django_db
def test_invalid_json_is_rejected(client):
    response = client.post("/api/routes/", "{not json", content_type="application/json")

    assert response.status_code == 400
    assert response.json()["details"] == {"body": "Invalid JSON."}


def test_list_is_paginated_with_20_routes_per_page(client, make_route):
    for i in range(25):
        make_route(name=f"Route {i}")

    first = client.get("/api/routes/").json()
    second = client.get("/api/routes/?page=2").json()

    assert first["count"] == 25
    assert first["page_size"] == 20
    assert len(first["results"]) == 20
    assert len(second["results"]) == 5
    assert second["results"][0]["name"] == "Route 20"


@pytest.mark.django_db
def test_invalid_page_is_rejected(client):
    response = client.get("/api/routes/?page=0")

    assert response.status_code == 400


@pytest.mark.django_db
def test_route_includes_estimated_duration(client):
    payload = {**VALID_ROUTE, "distance": 12, "elevation_gain_m": 600}

    body = client.post("/api/routes/", payload, content_type="application/json").json()

    assert body["estimated_duration_min"] == 240
