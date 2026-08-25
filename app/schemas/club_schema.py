from app.utils.error_handlers import APIError
from app.utils.validators import require_fields


def club_to_dict(club):
    return {
        "id": club.id,
        "name": club.name,
        "genre": club.genre,
        "description": club.description,
        "created_by": club.created_by,
        "created_at": club.created_at.isoformat(),
    }


def validate_club_payload(data, *, partial=False):
    """`partial=True` for updates (PUT), where fields are optional but
    whatever is present still has to be valid."""
    if not partial:
        require_fields(data, "name", "genre")

    name = data.get("name")
    genre = data.get("genre")

    if name is not None and not str(name).strip():
        raise APIError("name cannot be empty", 400)
    if genre is not None and not str(genre).strip():
        raise APIError("genre cannot be empty", 400)

    cleaned = {}
    if name is not None:
        cleaned["name"] = str(name).strip()
    if genre is not None:
        cleaned["genre"] = str(genre).strip()
    if "description" in data:
        cleaned["description"] = data["description"]

    return cleaned
