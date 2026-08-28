"""
app/services/movies_service.py

All TMDB API access lives here. The route layer never calls `requests`
or knows TMDB's URL shape directly -- it asks this service for domain
objects (MovieSummary / MovieDetail) and turns those into JSON via the
schemas. Pulling this out of routes/movies.py makes the TMDB integration
unit-testable (inject a fake `session`, no Flask app needed) and gives a
single place to add caching or rate limiting later without touching the
route handlers.
"""

import requests
from flask import current_app

from app.models.movie import CastMember, MovieDetail, MovieSummary

TMDB_BASE_URL = 'https://api.themoviedb.org/3'
TMDB_IMAGE_BASE = 'https://image.tmdb.org/t/p'


class MovieNotFoundError(Exception):
    """Raised when TMDB returns 404 for a given id."""


class MovieServiceUnavailableError(Exception):
    """Raised for network errors, timeouts, or non-404 HTTP errors."""


class MovieService:
    def __init__(self, session=None):
        # Allows tests to pass in a fake session instead of hitting TMDB.
        self._session = session or requests

    def _get(self, path, params=None):
        params = dict(params or {})
        params['api_key'] = current_app.config['TMDB_API_KEY']
        try:
            resp = self._session.get(
                f'{TMDB_BASE_URL}{path}', params=params, timeout=5)
            resp.raise_for_status()
        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                raise MovieNotFoundError from e
            raise MovieServiceUnavailableError from e
        except requests.RequestException as e:
            raise MovieServiceUnavailableError from e
        return resp.json()

    @staticmethod
    def _poster_url(poster_path, size='w342'):
        return f'{TMDB_IMAGE_BASE}/{size}{poster_path}' if poster_path else None

    def search(self, query, limit=10):
        data = self._get(
            '/search/movie', {'query': query, 'include_adult': 'false'})
        return [
            MovieSummary(
                tmdb_id=r['id'],
                title=r.get('title'),
                year=(r.get('release_date') or '')[:4] or None,
                poster_url=self._poster_url(r.get('poster_path'), 'w185'),
            )
            for r in data.get('results', [])[:limit]
        ]

    def trending(self, limit=10):
        data = self._get('/trending/movie/week')
        return [
            MovieSummary(
                tmdb_id=r['id'],
                title=r.get('title'),
                year=(r.get('release_date') or '')[:4] or None,
                poster_url=self._poster_url(r.get('poster_path'), 'w185'),
            )
            for r in data.get('results', [])[:limit]
        ]

    def get(self, tmdb_id, cast_limit=6):
        data = self._get(f'/movie/{tmdb_id}',
                         {'append_to_response': 'credits'})

        cast = [
            CastMember(
                name=c['name'],
                character=c.get('character'),
                profile_url=self._poster_url(c.get('profile_path'), 'w185'),
            )
            for c in data.get('credits', {}).get('cast', [])[:cast_limit]
        ]

        return MovieDetail(
            tmdb_id=data['id'],
            title=data.get('title'),
            year=(data.get('release_date') or '')[:4] or None,
            runtime=data.get('runtime'),
            genres=[g['name'] for g in data.get('genres', [])],
            overview=data.get('overview'),
            rating=data.get('vote_average'),
            poster_url=self._poster_url(data.get('poster_path'), 'w500'),
            backdrop_url=self._poster_url(data.get('backdrop_path'), 'w1280'),
            cast=cast,
        )
