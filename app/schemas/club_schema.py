from app.utils.error_handlers import APIError
from app.utils.validators import require_fields


def club_to_dict(club, current_user_id=None):
    """
    Convert a Club model into a JSON-friendly dictionary.

    current_user_id is optional so the same serializer can be used
    for public requests and authenticated requests.
    """

    members = getattr(club, "members", []) or []
    posts = getattr(club, "posts", []) or []

    current_membership = None

    if current_user_id is not None:
        current_membership = next(
            (
                member
                for member in members
                if member.user_id == current_user_id
            ),
            None,
        )

    return {
        "id": club.id,
        "name": club.name,
        "genre": club.genre,
        "description": club.description,
        "text": club.description,
        "background_url": club.background_url,
        "club_text": club.description,

        # Creator/founder
        "created_by": club.created_by,

        # Dates
        "created_at": club.created_at.isoformat(),

        # Counts
        "member_count": len(members),
        "post_count": len(posts),

        # Current user's membership
        "is_member": current_membership is not None,
        "is_admin": (
            current_membership is not None
            and current_membership.role == "admin"
        ),
    }


def validate_club_payload(data, *, partial=False):
    """
    Validate and clean club creation/update data.

    partial=True is used when updating a club, where fields are optional.
    """

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

    for field_name, target_name in (
        ("description", "description"),
        ("text", "description"),
        ("club_text", "description"),
        ("background_url", "background_url"),
        ("backgroundImageUrl", "background_url"),
        ("cover_image", "background_url"),
        ("coverImage", "background_url"),
    ):
        if field_name not in data:
            continue

        value = data[field_name]

        if value is not None:
            value = str(value).strip()

        cleaned[target_name] = value

    return cleaned
