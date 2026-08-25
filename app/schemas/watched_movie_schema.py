from app.utils.error_handlers import APIError
from app.utils.validators import require_fields, parse_iso_date


def watched_movie_to_dict(entry):
    return {
        "id": entry.id,
        "user_id": entry.user_id,
        "movie_title": entry.movie_title,
        "watched_date": entry.watched_date.isoformat() if entry.watched_date else None,
        "personal_rating": entry.personal_rating,
        "notes": entry.notes,
        "created_at": entry.created_at.isoformat(),
    }


def validate_watched_movie_payload(data):
    require_fields(data, "movie_title")

    movie_title = str(data["movie_title"]).strip()
    if not movie_title:
        raise APIError("movie_title cannot be empty", 400)

    rating = data.get("personal_rating")
    if rating is not None and (not isinstance(rating, int) or isinstance(rating, bool) or not (1 <= rating <= 5)):
        raise APIError("personal_rating must be an integer between 1 and 5", 400)

    return {
        "movie_title": movie_title,
        "watched_date": parse_iso_date(data.get("watched_date"), "watched_date"),
        "personal_rating": rating,
        "notes": data.get("notes"),
    }
