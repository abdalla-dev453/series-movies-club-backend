"""Authorization helpers shared across blueprints.

Two concerns live here: identifying who's making the request, and
answering club-scoped "is this person allowed to..." questions. Every
permission check in the app goes through `ClubMember.role` -- see
`Club.created_by` in the model for why that column is deliberately
*not* used for authorization.
"""

from flask_jwt_extended import get_jwt_identity
from app.extensions import db
from app.utils.error_handlers import APIError
from app.models import ClubMember, User
from functools import wraps

ADMIN_ROLE = "admin"
MEMBER_ROLE = "member"


def get_current_user():
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id)) if user_id is not None else None
    if user is None:
        raise APIError("User not found", 401)
    return user


def get_membership(user_id, club_id):
    return ClubMember.query.filter_by(user_id=user_id, club_id=club_id).first()


def is_club_admin(user_id, club_id):
    membership = get_membership(user_id, club_id)
    return membership is not None and membership.role == ADMIN_ROLE


def is_club_member(user_id, club_id):
    return get_membership(user_id, club_id) is not None


def require_club_admin(user_id, club_id):
    if not is_club_admin(user_id, club_id):
        raise APIError("Only club admins can do this", 403)


def require_club_member(user_id, club_id):
    if not is_club_member(user_id, club_id):
        raise APIError("You must be a club member to do this", 403)


def require_owner(resource_user_id, current_user_id, message="You don't own this resource"):
    if resource_user_id != current_user_id:
        raise APIError(message, 403)

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        get_current_user()
        return f(*args, **kwargs)
    return wrapper
