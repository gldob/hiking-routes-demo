import hmac
from functools import wraps

from django.conf import settings
from django.http import JsonResponse

SAFE_METHODS = ("GET", "HEAD", "OPTIONS")


def token_required_for_writes(view):
    """Reject non-read requests unless the X-API-Token header matches API_TOKEN."""

    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if request.method not in SAFE_METHODS:
            supplied = request.headers.get("X-API-Token", "")
            if not hmac.compare_digest(supplied.encode(), settings.API_TOKEN.encode()):
                return JsonResponse(
                    {"error": "unauthorized", "detail": "Missing or invalid X-API-Token header."},
                    status=401,
                )
        return view(request, *args, **kwargs)

    return wrapper
