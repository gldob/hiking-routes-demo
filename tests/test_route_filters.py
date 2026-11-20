import pytest


@pytest.fixture
def routes(make_route):
    make_route(name="Easy short", difficulty="T1", distance_km=4.0)
    make_route(name="Medium short", difficulty="T2", distance_km=9.5)
    make_route(name="Medium exactly ten", difficulty="T2", distance_km=10.0)
    make_route(name="Medium long", difficulty="T2", distance_km=18.0)
    make_route(name="Hard short", difficulty="T4", distance_km=6.0)


def names(response):
    return [route["name"] for route in response.json()["results"]]


def test_filter_by_difficulty(client, routes):
    response = client.get("/api/routes/?difficulty=T2")

    assert response.status_code == 200
    assert names(response) == ["Medium short", "Medium exactly ten", "Medium long"]
    assert response.json()["count"] == 3


def test_filter_by_max_distance_includes_the_limit(client, routes):
    response = client.get("/api/routes/?max_distance=10")

    assert names(response) == ["Easy short", "Medium short", "Medium exactly ten", "Hard short"]


def test_filters_combine(client, routes):
    response = client.get("/api/routes/?difficulty=T2&max_distance=10")

    assert names(response) == ["Medium short", "Medium exactly ten"]


@pytest.mark.parametrize("query", ["difficulty=T9", "max_distance=ten"])
def test_invalid_filter_is_rejected(client, routes, query):
    response = client.get(f"/api/routes/?{query}")

    assert response.status_code == 400
    assert response.json()["error"] == "validation_failed"
