import re
from datetime import datetime

from app.utils.error_handlers import APIError

USERNAME_MIN_LEN = 3
PASSWORD_MIN_LEN = 8
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
RATING_RANGE = range(1, 6)


def get_json_body():
    from flask import request

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise APIError("Request body must be a JSON object", 400)
    return data


def require_fields(data, *fields):
    missing = [ f for f in fields if not data.get(f)]
    if missing:
        raise APIError(f"Missing required fields: {', '.join(missing)}", 400)


def validate_signup_payload(data):
    require_fields(data, "username", "email", "password")

    username = str(data.get("username")).strip()
    if len(username) < USERNAME_MIN_LEN:
        raise APIError("Username must be at least 3 characters long", 400)

    email = str(data.get("email")).strip().lower()
    if not EMAIL_RE.match(email):
        raise APIError("Invalid email address", 400)

    password = str(data.get("password"))
    if len(password) < PASSWORD_MIN_LEN:
        raise APIError("Password must be at least 8 characters long", 400)

    return username, email, password


def validate_rating(value):
    if not isinstance(value, int) or isinstance(value, bool) or value not in RATING_RANGE:
        raise APIError("Rating mustt be an integer between 1 and 5", 400)
    return value


def parse_iso_date(value, field_name="date"):
    """A strict YYYY-MM-DD string into date"""
    if value in (None, ""):
        return None
    if not isinstance(`value`, str):
        raise APIError(f"Invalid {field_name} format expected YYYY-MM-DD", 400)
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise APIError(f"Invalid {field_name} format expected YYYY-MM-DD", 400)


def validate_pagination_params(args):
    """Parsing ?page & ?per_page params"""
    try:
        page = int(args.get("page", 1))
        per_page = int(args.get("per_page", 20))
    except (TypeError, ValueError):
        raise APIError("Page and per_page must be integers", 400)

    if page < 1 or per_page < 1:
        raise APIError("Page and per_page must be positive integers", 400)

    return page, min(per_page, 100)