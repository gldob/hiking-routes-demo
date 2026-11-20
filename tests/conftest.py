import pytest

from routes.models import Route


@pytest.fixture
def make_route(db):
    def make(**overrides):
        fields = {
            "name": "Hoher Kasten",
            "region": "Appenzell",
            "distance_km": 8.5,
            "elevation_gain_m": 650,
            "difficulty": "T2",
        }
        fields.update(overrides)
        return Route.objects.create(**fields)

    return make
