"""Business logic for clubs and club membership.

Kept out of the blueprint so the HTTP layer only deals with request/response
concerns -- every function here takes plain values in and returns model
instances (or raises APIError), with no knowledge of Flask.
"""

from app.extensions import db
from app.models import Club, ClubMember
from app.utils.error_handlers import APIError
from app.utils.permissions import ADMIN_ROLE, MEMBER_ROLE, get_membership, is_club_admin


def create_club(creator, name, genre, description=None):
    club = Club(name=name, genre=genre, description=description, created_by=creator.id)
    db.session.add(club)
    db.session.flush()  # assigns club.id without committing yet

    membership = ClubMember(club_id=club.id, user_id=creator.id, role=ADMIN_ROLE)
    db.session.add(membership)
    db.session.commit()
    return club


def list_clubs(page, per_page):
    pagination = Club.query.order_by(Club.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return pagination


def update_club(club, current_user_id, fields):
    if not is_club_admin(current_user_id, club.id):
        raise APIError("Only club admins can update this club", 403)

    for key, value in fields.items():
        setattr(club, key, value)
    db.session.commit()
    return club


def join_club(club, user):
    if get_membership(user.id, club.id) is not None:
        raise APIError("Already a member of this club", 409)

    membership = ClubMember(club_id=club.id, user_id=user.id, role=MEMBER_ROLE)
    db.session.add(membership)
    db.session.commit()
    return membership


def leave_club(club, user):
    membership = get_membership(user.id, club.id)
    if membership is None:
        raise APIError("Not a member of this club", 404)

    if membership.role == ADMIN_ROLE and _admin_count(club.id) <= 1:
        raise APIError("The last admin cannot leave the club", 400)

    db.session.delete(membership)
    db.session.commit()


def update_member_role(club, current_user_id, target_user_id, new_role):
    if new_role not in (ADMIN_ROLE, MEMBER_ROLE):
        raise APIError("role must be 'admin' or 'member'", 400)

    if not is_club_admin(current_user_id, club.id):
        raise APIError("Only club admins can change member roles", 403)

    membership = get_membership(target_user_id, club.id)
    if membership is None:
        raise APIError("That user is not a member of this club", 404)

    if membership.role == ADMIN_ROLE and new_role == MEMBER_ROLE and _admin_count(club.id) <= 1:
        raise APIError("The last admin cannot be demoted", 400)

    membership.role = new_role
    db.session.commit()
    return membership


def remove_member(club, current_user_id, target_user_id):
    if not is_club_admin(current_user_id, club.id):
        raise APIError("Only club admins can remove members", 403)

    membership = get_membership(target_user_id, club.id)
    if membership is None:
        raise APIError("That user is not a member of this club", 404)

    if membership.role == ADMIN_ROLE and _admin_count(club.id) <= 1:
        raise APIError("The last admin cannot be removed", 400)

    db.session.delete(membership)
    db.session.commit()


def _admin_count(club_id):
    return ClubMember.query.filter_by(club_id=club_id, role=ADMIN_ROLE).count()