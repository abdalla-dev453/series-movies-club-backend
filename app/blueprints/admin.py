from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models import Club, Post, User
from app.schemas.club_schema import club_to_dict
from app.schemas.user_schema import user_to_private_dict
from app.utils.decorators import get_or_404
from app.utils.permissions import require_superuser


admin_bp = Blueprint("admin", __name__)


def admin_endpoint(function):
    @jwt_required()
    def protected(*args, **kwargs):
        require_superuser()
        return function(*args, **kwargs)

    protected.__name__ = function.__name__
    return protected


@admin_bp.get("/stats")
@admin_endpoint
def stats():
    return jsonify({
        "totalUsers": User.query.count(),
        "totalClubs": Club.query.count(),
        "totalPosts": Post.query.count(),
        "flaggedContent": 0,
        "systemStatus": "Healthy",
        "activeSessions": 0,
    })


@admin_bp.get("/users")
@admin_endpoint
def users():
    query = request.args.get("query", "").strip()
    user_query = User.query.order_by(User.username.asc())
    if query:
        user_query = user_query.filter(User.username.ilike(f"%{query}%"))
    return jsonify({"users": [user_to_private_dict(user) for user in user_query.all()]})


@admin_bp.patch("/users/<int:user_id>/role")
@admin_endpoint
def update_role(user_id):
    user = get_or_404(User, user_id)
    payload = request.get_json(silent=True) or {}
    user.is_superuser = bool(payload.get("is_superuser", False))
    db.session.commit()
    return jsonify(user_to_private_dict(user))


@admin_bp.patch("/users/<int:user_id>/status")
@admin_endpoint
def update_status(user_id):
    user = get_or_404(User, user_id)
    payload = request.get_json(silent=True) or {}
    user.is_banned = bool(payload.get("is_banned", False))
    db.session.commit()
    return jsonify(user_to_private_dict(user))


@admin_bp.get("/clubs")
@admin_endpoint
def clubs():
    return jsonify({"clubs": [club_to_dict(club) for club in Club.query.order_by(Club.name.asc()).all()]})


@admin_bp.delete("/clubs/<int:club_id>")
@admin_endpoint
def delete_club(club_id):
    club = get_or_404(Club, club_id)
    db.session.delete(club)
    db.session.commit()
    return jsonify({"message": "Club deleted"})


@admin_bp.get("/moderation")
@admin_endpoint
def moderation():
    return jsonify([])


@admin_bp.delete("/posts/<int:post_id>")
@admin_endpoint
def delete_post(post_id):
    post = get_or_404(Post, post_id)
    db.session.delete(post)
    db.session.commit()
    return jsonify({"message": "Post deleted"})


@admin_bp.get("/settings")
@admin_endpoint
def settings():
    return jsonify({
        "maintenanceMode": False,
        "allowNewSignups": True,
        "requireEmailVerification": True,
        "maxClubsPerUser": 5,
    })


@admin_bp.put("/settings")
@admin_endpoint
def update_settings():
    return jsonify(request.get_json(silent=True) or {})
