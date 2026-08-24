"""
app/routes/movies.py

Proxies The Movie Database (TMDB) API so:
  1. TMDB_API_KEY never reaches the browser (frontend calls our backend, not TMDB directly)
  2. We control caching / rate limiting in one place
  3. Response shape is normalized to only what the frontend actually needs

No new table is added for this -- we don't duplicate TMDB's catalog into our DB.
The only schema change is posts.tmdb_id (nullable int), added via migration,
so a post can reference a specific movie without storing its metadata redundantly.

Route handlers here are intentionally thin: they validate input, delegate to
MovieService, and shape the response with the marshmallow schemas. All TMDB
request/response details live in app/services/movies_service.py.
"""

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from app.utils.permissions import login_required
from app.schemas.movies import MovieSearchResponseSchema, MovieDetailSchema
from app.services.movies_service import (
    MovieService,
    MovieNotFoundError,
    MovieServiceUnavailableError,
)

movies_bp = Blueprint('movies', __name__)
movie_service = MovieService()


@movies_bp.route('/movies/search', methods=['GET'])
@login_required
def search_movies():
    query = request.args.get('query', '').strip()
    if not query:
        return jsonify({'items': []})

    try:
        results = movie_service.search(query)
    except MovieServiceUnavailableError:
        return jsonify({'error': 'Could not reach movie database'}), 502

    return jsonify(MovieSearchResponseSchema().dump({'items': results}))


@movies_bp.route('/movies/<int:tmdb_id>', methods=['GET'])
@login_required
def get_movie(tmdb_id):
    try:
        movie = movie_service.get(tmdb_id)
    except MovieNotFoundError:
        return jsonify({'error': 'Movie not found'}), 404
    except MovieServiceUnavailableError:
        return jsonify({'error': 'Could not reach movie database'}), 502

    return jsonify(MovieDetailSchema().dump(movie))
