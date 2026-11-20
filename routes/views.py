import json

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_http_methods

from routes.models import Rating, Route
from routes.validation import ValidationError, validate_rating, validate_route

PAGE_SIZE = 10


def _error(status, error, **extra):
    return JsonResponse({"error": error, **extra}, status=status)


def _parse_json(request):
    try:
        return json.loads(request.body or b"null")
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise ValidationError({"body": "Invalid JSON."})


@require_http_methods(["GET", "POST"])
def route_collection(request):
    if request.method == "POST":
        return _create_route(request)
    return _list_routes(request)


def _parse_list_params(params):
    """Read ?page, ?difficulty and ?max_distance from the query string."""
    errors = {}
    filters = {}

    try:
        page = int(params.get("page", "1"))
        if page < 1:
            raise ValueError
    except ValueError:
        errors["page"] = "Must be a positive integer."
        page = None

    difficulty = params.get("difficulty")
    if difficulty is not None:
        if difficulty in Route.Difficulty.values:
            filters["difficulty"] = difficulty
        else:
            errors["difficulty"] = "Must be one of " + ", ".join(Route.Difficulty.values) + "."

    max_distance = params.get("max_distance")
    if max_distance is not None:
        try:
            filters["distance_km__lte"] = float(max_distance)
        except ValueError:
            errors["max_distance"] = "Must be a number."

    if errors:
        raise ValidationError(errors)
    return page, filters


def _list_routes(request):
    try:
        page, filters = _parse_list_params(request.GET)
    except ValidationError as exc:
        return _error(400, "validation_failed", details=exc.errors)

    routes = Route.objects.with_rating_stats().filter(**filters)
    offset = (page - 1) * PAGE_SIZE
    page_routes = routes[offset : offset + PAGE_SIZE]
    return JsonResponse(
        {
            "count": routes.count(),
            "page": page,
            "page_size": PAGE_SIZE,
            "results": [route.to_dict() for route in page_routes],
        }
    )


def _create_route(request):
    try:
        fields = validate_route(_parse_json(request))
    except ValidationError as exc:
        return _error(400, "validation_failed", details=exc.errors)
    route = Route.objects.create(**fields)
    return JsonResponse(route.to_dict(), status=201)


@require_GET
def route_detail(request, route_id):
    route = Route.objects.with_rating_stats().filter(pk=route_id).first()
    if route is None:
        return _error(404, "not_found")
    return JsonResponse(route.to_dict())


@require_http_methods(["GET", "POST"])
def route_ratings(request, route_id):
    route = Route.objects.filter(pk=route_id).first()
    if route is None:
        return _error(404, "not_found")

    if request.method == "POST":
        try:
            fields = validate_rating(_parse_json(request))
        except ValidationError as exc:
            return _error(400, "validation_failed", details=exc.errors)
        rating = Rating.objects.create(route=route, **fields)
        return JsonResponse(rating.to_dict(), status=201)

    return JsonResponse({"results": [rating.to_dict() for rating in route.ratings.all()]})
