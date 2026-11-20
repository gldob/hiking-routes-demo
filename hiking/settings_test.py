"""Settings for the test suite: provides dummy values for required variables."""

import os

os.environ.setdefault("DJANGO_SECRET_KEY", "test-secret-key")
os.environ.setdefault("API_TOKEN", "test-token")

from hiking.settings import *  # noqa: E402,F401,F403
