from routes.models import Route


class ValidationError(Exception):
    def __init__(self, errors):
        super().__init__(errors)
        self.errors = errors


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _required_text(data, field, max_length, errors):
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        errors[field] = "This field is required."
        return None
    if len(value.strip()) > max_length:
        errors[field] = f"At most {max_length} characters."
    return value.strip()


def validate_route(data):
    """Validate a JSON payload for a new route and return the cleaned fields."""
    if not isinstance(data, dict):
        raise ValidationError({"body": "Expected a JSON object."})

    errors = {}
    name = _required_text(data, "name", 200, errors)
    region = _required_text(data, "region", 100, errors)

    distance_km = data.get("distance_km")
    if not _is_number(distance_km):
        errors["distance_km"] = "Must be a number."

    elevation_gain_m = data.get("elevation_gain_m")
    if not isinstance(elevation_gain_m, int) or isinstance(elevation_gain_m, bool):
        errors["elevation_gain_m"] = "Must be an integer."
    elif elevation_gain_m < 0:
        errors["elevation_gain_m"] = "Must not be negative."

    difficulty = data.get("difficulty")
    if difficulty not in Route.Difficulty.values:
        errors["difficulty"] = "Must be one of " + ", ".join(Route.Difficulty.values) + "."

    if errors:
        raise ValidationError(errors)

    return {
        "name": name,
        "region": region,
        "distance_km": float(distance_km),
        "elevation_gain_m": elevation_gain_m,
        "difficulty": difficulty,
    }
