"""Business logic for the follower/followee graph."""

from app.extensions import db
from app.models import Follow, User
from app.utils.error_handlers import APIError


def follow_user(follower, followee):
    if follower.id == followee.id:
        raise APIError("You cannot follow yourself", 400)

    exists = Follow.query.filter_by(
        follower_id=follower.id, followee_id=followee.id
    ).first()
    if exists is not None:
        raise APIError("Already following this user", 409)

    follow = Follow(follower_id=follower.id, followee_id=followee.id)
    db.session.add(follow)
    db.session.commit()
    return follow


def unfollow_user(follower, followee):
    follow = Follow.query.filter_by(
        follower_id=follower.id, followee_id=followee.id
    ).first()
    if follow is None:
        raise APIError("You are not following this user", 404)

    db.session.delete(follow)
    db.session.commit()


def list_followers(user):
    return [f.follower for f in user.followers]


def list_following(user):
    return [f.followee for f in user.following]


def list_mutual(user):
    follower_ids = {follow.follower_id for follow in user.followers}
    followee_ids = {follow.followee_id for follow in user.following}
    mutual_ids = follower_ids & followee_ids

    if not mutual_ids:
        return []

    return User.query.filter(User.id.in_(mutual_ids)).all()
