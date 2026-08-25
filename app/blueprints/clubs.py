from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.models import Club
from app.schemas.club_schema import club_to_dict, validate_club_payload
from app.services.club_service import create_club, list_clubs, update_club
from app.utils.decorators import get_or_404
from app.utils.permissions import get_current_user
from app.utils.validators import get_json_body, validate_pagination_params

clubs_bp = Blueprint("clubs", __name__, url_prefix="/clubs")


@clubs_bp.get("")
def index():
    page, per_page = validate_pagination_params(request.args)
    pagination = list_clubs(page, per_page)
    return jsonify(
        {
            "items": [club_to_dict(c) for c in pagination.items],
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
        current_user, fields["name"], fields["genre"], fields.get("description")
    )
    return jsonify(club_to_dict(club)), 201


@clubs_bp.get("/<int:club_id>")
def get_club(club_id):
    club = get_or_404(Club, club_id)
    return jsonify(club_to_dict(club)), 200


@clubs_bp.put("/<int:club_id>")
@jwt_required()
def update(club_id):
    current_user = get_current_user()
    club = get_or_404(Club, club_id)
    data = get_json_body()
    fields = validate_club_payload(data, partial=True)
    club = update_club(club, current_user.id, fields)
    return jsonify(club_to_dict(club)), 200
