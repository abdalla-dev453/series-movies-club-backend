from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required, verify_jwt_in_request

from app.models import Club, ClubMember
from app.schemas.club_schema import club_to_dict, validate_club_payload
from app.services.club_service import create_club, list_clubs, update_club
from app.utils.decorators import get_or_404
from app.utils.permissions import get_current_user
from app.utils.validators import get_json_body, validate_pagination_params

clubs_bp = Blueprint("clubs", __name__, url_prefix="/clubs")


@clubs_bp.get("")
def index():
    verify_jwt_in_request(optional=True)
    current_user_id = get_jwt_identity()
    page, per_page = validate_pagination_params(request.args)
    pagination = list_clubs(page, per_page)
    return jsonify(
        {
            "items": [_club_response(c, current_user_id) for c in pagination.items],
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total_items": pagination.total,
            "total_pages": pagination.pages,
        }
    ), 200


@clubs_bp.post("")
@jwt_required()
def create():
    current_user = get_current_user()
    data = get_json_body()
    fields = validate_club_payload(data)
    club = create_club(
        current_user, fields["name"], fields["genre"], fields.get(
            "description")
    )
    return jsonify(club_to_dict(club)), 201


@clubs_bp.get("/<int:club_id>")
def get_club(club_id):
    verify_jwt_in_request(optional=True)
    current_user_id = get_jwt_identity()
    club = get_or_404(Club, club_id)
    return jsonify(_club_response(club, current_user_id)), 200


def _club_response(club, current_user_id):
    data = club_to_dict(club)
    data["member_count"] = ClubMember.query.filter_by(club_id=club.id).count()
    membership = ClubMember.query.filter_by(
        club_id=club.id, user_id=int(current_user_id)
    ).first() if current_user_id is not None else None
    data["is_member"] = membership is not None
    data["is_admin"] = membership is not None and membership.role == "admin"
    return data


@clubs_bp.put("/<int:club_id>")
@jwt_required()
def update(club_id):
    current_user = get_current_user()
    club = get_or_404(Club, club_id)
    data = get_json_body()
    fields = validate_club_payload(data, partial=True)
    club = update_club(club, current_user.id, fields)
    return jsonify(club_to_dict(club)), 200
