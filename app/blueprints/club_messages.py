from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models import Club, ClubMessage
from app.schemas.club_message_schema import club_message_to_dict, validate_club_message_payload
from app.utils.decorators import get_or_404
from app.utils.error_handlers import APIError
from app.utils.permissions import get_current_user, is_club_admin, is_club_member
from app.utils.validators import get_json_body

club_messages_bp = Blueprint("club_messages", __name__, url_prefix="/clubs")


@club_messages_bp.get("/<int:club_id>/messages")
@jwt_required()
def list_messages(club_id):
    current_user = get_current_user()
    club = get_or_404(Club, club_id)
    if not is_club_member(current_user.id, club.id):
        raise APIError(
            "You must be a member of this club to view messages", 403)

    messages = ClubMessage.query.filter_by(
        club_id=club.id).order_by(ClubMessage.created_at.asc()).all()
    return jsonify([club_message_to_dict(message) for message in messages]), 200


@club_messages_bp.post("/<int:club_id>/messages")
@jwt_required()
def create_message(club_id):
    current_user = get_current_user()
    club = get_or_404(Club, club_id)
    if not is_club_member(current_user.id, club.id):
        raise APIError(
            "You must be a member of this club to post messages", 403)

    data = get_json_body()
    fields = validate_club_message_payload(data)

    message = ClubMessage(
        club_id=club.id,
        user_id=current_user.id,
        message=fields["message"],
    )
    db.session.add(message)
    db.session.commit()

    return jsonify(club_message_to_dict(message)), 201


@club_messages_bp.delete("/<int:club_id>/messages/<int:message_id>")
@jwt_required()
def delete_message(club_id, message_id):
    current_user = get_current_user()
    club = get_or_404(Club, club_id)
    message = get_or_404(ClubMessage, message_id)

    if message.club_id != club.id:
        raise APIError("This message is not in this club", 400)

    can_delete = (
        message.user_id == current_user.id
        or is_club_admin(current_user.id, club.id)
    )
    if not can_delete:
        raise APIError(
            "You can only delete your own club messages or admin-managed messages", 403)

    db.session.delete(message)
    db.session.commit()
    return "", 204
