"""
app/models/movie.py

Domain objects for TMDB movie data. These are plain dataclasses, not
SQLAlchemy models -- movie metadata is never persisted to our DB (see
app/routes/movies.py for why: we proxy TMDB rather than duplicating its
catalog). They give the service layer and schemas a typed shape to pass
around instead of raw TMDB dicts.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CastMember:
    name: str
    character: Optional[str]
    profile_url: Optional[str]


@dataclass
class MovieSummary:
    """Shape returned by search -- enough to render a result row."""
    tmdb_id: int
    title: Optional[str]
    year: Optional[str]
    poster_url: Optional[str]


@dataclass
class MovieDetail:
    """Shape returned by the single-movie endpoint."""
    tmdb_id: int
    title: Optional[str]
    year: Optional[str]
    runtime: Optional[int]
    genres: List[str]
    overview: Optional[str]
    rating: Optional[float]
    poster_url: Optional[str]
    backdrop_url: Optional[str]
    cast: List[CastMember] = field(default_factory=list)
