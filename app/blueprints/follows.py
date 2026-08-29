from flask import Blueprint, jsonify
from app.models.user import User
from app.services.follow_service import (
    follow_user,
    unfollow_user,
    list_followers,
    list_following,
)
from app.schemas.user_schema import serialize_user
from app.utils.permissions import login_required, get_current_user

follows_bp = Blueprint("follows", __name__, url_prefix="/users")


@follows_bp.post("/<int:user_id>/follow")
@login_required
def follow(user_id):
    current_user = get_current_user()
    followee = User.query.get_or_404(user_id)

    follow = follow_user(current_user, followee)

    return jsonify({
        "message": "User followed successfully",
        "follower_id": follow.follower_id,
        "followee_id": follow.followee_id,
    }), 201


@follows_bp.delete("/<int:user_id>/follow")
@login_required
def unfollow(user_id):
    current_user = get_current_user()
    followee = User.query.get_or_404(user_id)

    unfollow_user(current_user, followee)

    return "", 204


@follows_bp.get("/<int:user_id>/followers")
def followers(user_id):
    user = User.query.get_or_404(user_id)

    users = list_followers(user)

    return jsonify([
        serialize_user(user)
        for user in users
    ]), 200


@follows_bp.get("/<int:user_id>/following")
def following(user_id):
    user = User.query.get_or_404(user_id)

    users = list_following(user)

    return jsonify([
        serialize_user(user)
        for user in users
    ]), 200