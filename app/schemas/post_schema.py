from app.utils.error_handlers import APIError
from app.utils.validators import require_fields


def post_to_dict(post):
    return {
        "id": post.id,
        "user_id": post.user_id,
        "club_id": post.club_id,
        "movie_title": post.movie_title,
        "tmdb_id": post.tmdb_id,
        "author_name": post.author.username if post.author else None,
        "description": post.description,
        "created_at": post.created_at.isoformat(),
        "review_count": len(post.reviews),
    }


def validate_post_payload(data):
    require_fields(data, "movie_title")

    movie_title = str(data["movie_title"]).strip()
    if not movie_title:
        raise APIError("movie_title cannot be empty", 400)

    club_id = data.get("club_id")
    if club_id is not None and not isinstance(club_id, int):
        raise APIError("club_id must be an integer", 400)

    return {
        "movie_title": movie_title,
        "description": data.get("description"),
        "tmdb_id": data.get("tmdb_id"),
        "club_id": club_id,
    }
