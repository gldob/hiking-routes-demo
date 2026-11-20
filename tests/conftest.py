import pytest
from django.conf import settings
from django.test import Client

from routes.models import Route


@pytest.fixture
def client():
    """Test client that sends a valid API token with every request."""
    return Client(headers={"X-API-Token": settings.API_TOKEN})


@pytest.fixture
def anonymous_client():
    return Client()


@pytest.fixture
def make_route(db):
    def make(**overrides):
        fields = {
            "name": "Hoher Kasten",
            "region": "Appenzell",
            "distance": 8.5,
            "elevation_gain_m": 650,
            "difficulty": "T2",
        }
        fields.update(overrides)
        return Route.objects.create(**fields)

    return make
