import pytest


def rate(client, route_id, **payload):
    return client.post(f"/api/routes/{route_id}/ratings/", payload, content_type="application/json")


def test_rating_a_route_returns_201(client, make_route):
    route = make_route()

    response = rate(client, route.id, stars=4, comment="Great view")

    assert response.status_code == 201
    body = response.json()
    assert body["route_id"] == route.id
    assert body["stars"] == 4
    assert body["comment"] == "Great view"


def test_route_shows_average_and_count(client, make_route):
    route = make_route()
    for stars in (5, 4, 4):
        rate(client, route.id, stars=stars)

    body = client.get(f"/api/routes/{route.id}/").json()

    assert body["rating_count"] == 3
    assert body["rating_average"] == 4.3


def test_unrated_route_has_no_average(client, make_route):
    route = make_route()

    body = client.get("/api/routes/").json()["results"][0]

    assert body["id"] == route.id
    assert body["rating_average"] is None
    assert body["rating_count"] == 0


def test_ratings_of_a_route_can_be_listed(client, make_route):
    route = make_route()
    other = make_route(name="Other")
    rate(client, route.id, stars=3)
    rate(client, other.id, stars=1)

    results = client.get(f"/api/routes/{route.id}/ratings/").json()["results"]

    assert [r["stars"] for r in results] == [3]


@pytest.mark.parametrize("stars", [0, 6, "5", None, 4.5])
def test_invalid_stars_are_rejected(client, make_route, stars):
    route = make_route()

    response = rate(client, route.id, stars=stars)

    assert response.status_code == 400
    assert "stars" in response.json()["details"]


@pytest.mark.django_db
def test_rating_an_unknown_route_returns_404(client):
    response = rate(client, 999, stars=5)

    assert response.status_code == 404
