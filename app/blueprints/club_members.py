from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from app.models import Club
from app.models.club_member import ClubMember
from app.schemas.club_member_schema import club_member_to_dict
from app.services.club_service import (
    join_club,
    leave_club,
    remove_member,
    update_member_role,
)
from app.utils.decorators import get_or_404
from app.utils.error_handlers import APIError
from app.utils.permissions import get_current_user
from app.utils.validators import get_json_body

club_members_bp = Blueprint("club_members", __name__, url_prefix="/clubs")


@club_members_bp.get("/<int:club_id>/members")
def list_members(club_id):
    get_or_404(Club, club_id)
    members = ClubMember.query.filter_by(club_id=club_id).all()
    return jsonify([club_member_to_dict(m) for m in members]), 200


@club_members_bp.post("/<int:club_id>/join")
@jwt_required()
def join(club_id):
    current_user = get_current_user()
    club = get_or_404(Club, club_id)
    membership = join_club(club, current_user)
    return jsonify(club_member_to_dict(membership)), 201


@club_members_bp.delete("/<int:club_id>/leave")
@jwt_required()
def leave(club_id):
    current_user = get_current_user()
    club = get_or_404(Club, club_id)
    leave_club(club, current_user)
    return "", 204


@club_members_bp.put("/<int:club_id>/members/<int:user_id>")
@jwt_required()
def update_role(club_id, user_id):
    current_user = get_current_user()
    club = get_or_404(Club, club_id)
    data = get_json_body()
    if "role" not in data:
        raise APIError("role is required", 400)

    membership = update_member_role(club, current_user.id, user_id, data["role"])
    return jsonify(club_member_to_dict(membership)), 200


@club_members_bp.delete("/<int:club_id>/members/<int:user_id>")
@jwt_required()
def remove(club_id, user_id):
    current_user = get_current_user()
    club = get_or_404(Club, club_id)
    remove_member(club, current_user.id, user_id)
    return "", 204
