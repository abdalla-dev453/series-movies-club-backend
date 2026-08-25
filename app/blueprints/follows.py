from flask import Blueprint, jsonify, abort

from app.extensions import db
from app.models.user import User
from app.models.follow import Follow
from app.schemas.user_schema import serialize_user
from app.utils.decorators import login_required, get_current_user

bp = Blueprint("follows", __name__, url_prefix="/users")


@bp.post("/<int:user_id>/follow")
@login_required
def follow_user(user_id):
    current = get_current_user()
    User.query.get_or_404(user_id)

    if current.id == user_id:
        abort(400, "Cannot follow yourself")

    if Follow.query.filter_by(follower_id=current.id, followee_id=user_id).first():
        abort(409, "Already following this user")

    db.session.add(Follow(follower_id=current.id, followee_id=user_id))
    db.session.commit()
    return "", 201


@bp.delete("/<int:user_id>/unfollow")
@login_required
def unfollow_user(user_id):
    current = get_current_user()
    follow = Follow.query.filter_by(follower_id=current.id, followee_id=user_id).first()
    if not follow:
        abort(404, "Not following this user")

    db.session.delete(follow)
    db.session.commit()
    return "", 204


@bp.get("/<int:user_id>/followers")
def list_followers(user_id):
    User.query.get_or_404(user_id)
    follows = Follow.query.filter_by(followee_id=user_id).all()
    return jsonify([serialize_user(f.follower) for f in follows])


@bp.get("/<int:user_id>/following")
def list_following(user_id):
    User.query.get_or_404(user_id)
    follows = Follow.query.filter_by(follower_id=user_id).all()
    return jsonify([serialize_user(f.followee) for f in follows])