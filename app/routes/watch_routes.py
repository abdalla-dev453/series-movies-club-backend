from marshmallow import ValidationError
from flask import Blueprint, current_app, jsonify, request

from app.schemas.watch_schema import CountryQuerySchema, WatchResponseSchema, WatchProvidersSchema
from app.services.tmdb_watch_service import (
    TMDBMovieNotFound, TMDBRateLimitError, TMDBUnavailableError, TMDBWatchService,
)
from app.utils.permissions import login_required

watch_bp = Blueprint("watch", __name__)
watch_service = TMDBWatchService()
country_schema = CountryQuerySchema()


def _country():
    try:
        values = country_schema.load({"country": request.args["country"]}) if "country" in request.args else {}
    except ValidationError:
        return None, (jsonify({"error": "country must be a two-letter uppercase country code"}), 400)
    country = values.get("country") or str(current_app.config.get("TMDB_DEFAULT_WATCH_REGION", "US")).upper()
    try:
        country_schema.fields["country"].validate(country)
    except ValidationError:
        return None, (jsonify({"error": "country must be a two-letter uppercase country code"}), 400)
    return country, None


def _error_response(error):
    if isinstance(error, TMDBMovieNotFound):
        return jsonify({"error": "Movie not found"}), 404
    if isinstance(error, TMDBRateLimitError):
        return jsonify({"error": "TMDB rate limit exceeded"}), 429
    return jsonify({"error": "Could not reach movie database"}), 502


@watch_bp.get("/<int:tmdb_id>/watch")
@login_required
def watch_movie(tmdb_id):
    country, error = _country()
    if error:
        return error
    try:
        result = watch_service.get_watch_data(tmdb_id, country)
    except (TMDBMovieNotFound, TMDBRateLimitError, TMDBUnavailableError) as exc:
        return _error_response(exc)
    return jsonify(WatchResponseSchema().dump(result))


@watch_bp.get("/<int:tmdb_id>/watch/providers")
@login_required
def watch_providers(tmdb_id):
    country, error = _country()
    if error:
        return error
    try:
        data = watch_service.get_providers_data(tmdb_id, country)
        mapped = watch_service._map_providers(data, tmdb_id, country)
    except (TMDBMovieNotFound, TMDBRateLimitError, TMDBUnavailableError) as exc:
        return _error_response(exc)
    return jsonify(WatchProvidersSchema().dump(mapped))
