from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models import Post
from app.schemas.post_schema import post_to_dict, validate_post_payload
from app.utils.decorators import get_or_404
from app.utils.error_handlers import APIError
from app.utils.permissions import get_current_user, is_club_admin, is_club_member
from app.utils.validators import get_json_body, validate_pagination_params

posts_bp = Blueprint("posts", __name__, url_prefix="/posts")


@posts_bp.get("")
def index():
    page, per_page = validate_pagination_params(request.args)
    pagination = Post.query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify(
        {
            "items": [post_to_dict(p) for p in pagination.items],
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total_items": pagination.total,
            "total_pages": pagination.pages,
        }
    ), 200


@posts_bp.post("")
@jwt_required()
def create():
    current_user = get_current_user()
    data = get_json_body()
    fields = validate_post_payload(data)

    club_id = fields["club_id"]
    if club_id is not None and not is_club_member(current_user.id, club_id):
        raise APIError("You must be a member of this club to post there", 403)

    post = Post(
        user_id=current_user.id,
        club_id=club_id,
        movie_title=fields["movie_title"],
        description=fields["description"],
    )
    db.session.add(post)
    db.session.commit()
    return jsonify(post_to_dict(post)), 201


@posts_bp.get("/<int:post_id>")
def get_post(post_id):
    post = get_or_404(Post, post_id)
    return jsonify(post_to_dict(post)), 200


@posts_bp.delete("/<int:post_id>")
@jwt_required()
def delete(post_id):
    current_user = get_current_user()
    post = get_or_404(Post, post_id)

    is_author = post.user_id == current_user.id
    is_admin_of_its_club = post.club_id is not None and is_club_admin(
        current_user.id, post.club_id
    )
    if not (is_author or is_admin_of_its_club):
        raise APIError("You can't delete this post", 403)

    db.session.delete(post)
    db.session.commit()
    return "", 204

