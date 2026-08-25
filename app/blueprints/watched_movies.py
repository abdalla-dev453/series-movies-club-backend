from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models import WatchedMovie
from app.schemas.watched_movie_schema import (
    validate_watched_movie_payload,
    watched_movie_to_dict,
)
from app.utils.decorators import get_or_404
from app.utils.permissions import get_current_user, require_owner
from app.utils.validators import get_json_body

watched_movies_bp = Blueprint("watched_movies", __name__, url_prefix="/watched")


@watched_movies_bp.get("")
@jwt_required()
def index():
    current_user = get_current_user()
    entries = (
        WatchedMovie.query.filter_by(user_id=current_user.id)
        .order_by(WatchedMovie.created_at.desc())
        .all()
    )
    return jsonify([watched_movie_to_dict(e) for e in entries]), 200


@watched_movies_bp.post("")
@jwt_required()
def create():
    current_user = get_current_user()
    data = get_json_body()
    fields = validate_watched_movie_payload(data)

    entry = WatchedMovie(user_id=current_user.id, **fields)
    db.session.add(entry)
    db.session.commit()
    return jsonify(watched_movie_to_dict(entry)), 201


@watched_movies_bp.delete("/<int:entry_id>")
@jwt_required()
def delete(entry_id):
    current_user = get_current_user()
    entry = get_or_404(WatchedMovie, entry_id)
    require_owner(entry.user_id, current_user.id, "You can only delete your own entries")

    db.session.delete(entry)
    db.session.commit()
    return "", 204
