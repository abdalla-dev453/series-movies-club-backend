from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.schemas.user_schema import user_to_private_dict, user_to_public_dict
from app.services.follow_service import follow_user, unfollow_user, list_followers, list_following
from app.utils.error_handlers import APIError
from app.utils.decorators import get_or_404
from app.utils.permissions import get_current_user, require_owner
from app.utils.validators import get_json_body
from app.models import User

users_bp = Blueprint("users", __name__, url_prefix="/users")

@users_bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = get_or_404(User, user_id)
    return jsonify(user_to_public_dict(user)), 200

@users_bp.route("/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    user = get_or_404(User, user_id)
    current_user = get_current_user()
    current_user_id = current_user.id
    require_owner(user.id, current_user_id, "You can only edit your own profile")


    data = get_json_body()
    for field in ("bio", "avatar_url"):
        if field in data:
            value = data[field]
            if value is not None and not isinstance(value, str):
                raise APIError(f"{field} must be a string", 400)
            setattr(user, field, value)
    db.session.commit()

    return jsonify(user_to_private_dict(current_user)), 200


@users_bp.post("/<int:user_id>/follow")
@jwt_required()
def follow(user_id):
    current_user = get_current_user()
    target = get_or_404(User, user_id)
    follow_user(current_user, target)
    return jsonify({"message": f"Now following {target.username}"}), 201


@users_bp.delete("/<int:user_id>/unfollow")
@jwt_required()
def unfollow(user_id):
    current_user = get_current_user()
    target = get_or_404(User, user_id)
    unfollow_user(current_user, target)
    return "", 204


@users_bp.get("/<int:user_id>/followers")
def followers(user_id):
    user = get_or_404(User, user_id)
    return jsonify([user_to_public_dict(u) for u in list_followers(user)]), 200


@users_bp.get("/<int:user_id>/following")
def following(user_id):
    user = get_or_404(User, user_id)
    return jsonify([user_to_public_dict(u) for u in list_following(user)]), 200
