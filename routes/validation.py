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

    distance = data.get("distance")
    if "distance_km" in data:
        errors["distance_km"] = "Renamed to 'distance' in version 2.0.0."
    if not _is_number(distance):
        errors["distance"] = "Must be a number."
    elif distance < 0:
        errors["distance"] = "Must not be negative."

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
        "distance": float(distance),
        "elevation_gain_m": elevation_gain_m,
        "difficulty": difficulty,
    }


def validate_rating(data):
    """Validate a JSON payload for a new rating and return the cleaned fields."""
    if not isinstance(data, dict):
        raise ValidationError({"body": "Expected a JSON object."})

    errors = {}
    stars = data.get("stars")
    if not isinstance(stars, int) or isinstance(stars, bool) or not 1 <= stars <= 5:
        errors["stars"] = "Must be an integer from 1 to 5."

    comment = data.get("comment", "")
    if not isinstance(comment, str):
        errors["comment"] = "Must be a string."
    elif len(comment) > 500:
        errors["comment"] = "At most 500 characters."

    if errors:
        raise ValidationError(errors)
    return {"stars": stars, "comment": comment.strip()}
