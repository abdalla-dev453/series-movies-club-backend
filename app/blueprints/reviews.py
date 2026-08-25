from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models import Post, Review
from app.schemas.review_schema import (
    review_to_dict,
    validate_review_create_payload,
    validate_review_update_payload,
)
from app.utils.decorators import get_or_404
from app.utils.error_handlers import APIError
from app.utils.permissions import get_current_user, require_owner
from app.utils.validators import get_json_body

reviews_bp = Blueprint("reviews", __name__, url_prefix="/reviews")


@reviews_bp.post("")
@jwt_required()
def create():
    current_user = get_current_user()
    data = get_json_body()
    fields = validate_review_create_payload(data)

    post = get_or_404(Post, fields["post_id"])
    if post.user_id == current_user.id:
        raise APIError("You can't review your own post", 403)

    existing = Review.query.filter_by(post_id=post.id, user_id=current_user.id).first()
    if existing is not None:
        raise APIError("You already reviewed this post", 409)

    review = Review(
        post_id=post.id,
        user_id=current_user.id,
        rating=fields["rating"],
        comment_text=fields["comment_text"],
    )
    db.session.add(review)
    db.session.commit()
    return jsonify(review_to_dict(review)), 201


@reviews_bp.get("/<int:review_id>")
def get_review(review_id):
    review = get_or_404(Review, review_id)
    return jsonify(review_to_dict(review)), 200


@reviews_bp.put("/<int:review_id>")
@jwt_required()
def update(review_id):
    current_user = get_current_user()
    review = get_or_404(Review, review_id)
    require_owner(review.user_id, current_user.id, "You can only edit your own review")

    data = get_json_body()
    fields = validate_review_update_payload(data)
    for key, value in fields.items():
        setattr(review, key, value)
    db.session.commit()
    return jsonify(review_to_dict(review)), 200


@reviews_bp.delete("/<int:review_id>")
@jwt_required()
def delete(review_id):
    current_user = get_current_user()
    review = get_or_404(Review, review_id)
    require_owner(review.user_id, current_user.id, "You can only delete your own review")

    db.session.delete(review)
    db.session.commit()
    return "", 204