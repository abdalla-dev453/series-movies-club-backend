from app.utils.error_handlers import APIError
from app.utils.validators import require_fields, validate_rating


def review_to_dict(review):
    return {
        "id": review.id,
        "post_id": review.post_id,
        "user_id": review.user_id,
        "author_name": review.author.username if review.author else None,
        "rating": review.rating,
        "comment_text": review.comment_text,
        "created_at": review.created_at.isoformat(),
        "updated_at": review.updated_at.isoformat() if review.updated_at else None,
    }


def validate_review_create_payload(data):
    require_fields(data, "post_id", "rating")

    post_id = data.get("post_id")
    if not isinstance(post_id, int):
        raise APIError("post_id must be an integer", 400)

    rating = validate_rating(data.get("rating"))

    return {
        "post_id": post_id,
        "rating": rating,
        "comment_text": data.get("comment_text"),
    }


def validate_review_update_payload(data):
    cleaned = {}
    if "rating" in data:
        cleaned["rating"] = validate_rating(data["rating"])
    if "comment_text" in data:
        cleaned["comment_text"] = data["comment_text"]
    if not cleaned:
        raise APIError("Nothing to update", 400)
    return cleaned
