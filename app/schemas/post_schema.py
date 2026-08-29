from app.utils.error_handlers import APIError
from app.utils.validators import require_fields


def post_to_dict(post):
    return {
        "id": post.id,
        "user_id": post.user_id,
        "club_id": post.club_id,
        "movie_title": post.movie_title,
        "description": post.description,
        "tmdb_id": post.tmdb_id,
        "created_at": post.created_at.isoformat(),
        "review_count": len(post.reviews),
    }


def validate_post_payload(data):
    require_fields(data, "movie_title")

    movie_title = str(data["movie_title"]).strip()

    if not movie_title:
        raise APIError("movie_title cannot be empty", 400)

    description = data.get("description")

    if description is not None and not isinstance(description, str):
        raise APIError("description must be a string", 400)

    if isinstance(description, str):
        description = description.strip()

    club_id = data.get("club_id")

    if club_id is not None:
        if not isinstance(club_id, int) or isinstance(club_id, bool):
            raise APIError("club_id must be an integer", 400)

    tmdb_id = data.get("tmdb_id")

    if tmdb_id is not None:
        if not isinstance(tmdb_id, int) or isinstance(tmdb_id, bool):
            raise APIError("tmdb_id must be an integer", 400)

    return {
        "movie_title": movie_title,
        "description": description,
        "club_id": club_id,
        "tmdb_id": tmdb_id,
    }