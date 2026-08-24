
from marshmallow import Schema, fields, validate


class MovieSearchQuerySchema(Schema):
    """Validates ?query= on GET /movies/search."""
    query = fields.String(required=True, validate=validate.Length(min=1, max=200))


class MovieSummarySchema(Schema):
    tmdb_id = fields.Int()
    title = fields.String(allow_none=True)
    year = fields.String(allow_none=True)
    poster_url = fields.String(allow_none=True)


class MovieSearchResponseSchema(Schema):
    items = fields.List(fields.Nested(MovieSummarySchema))


class CastMemberSchema(Schema):
    name = fields.String()
    character = fields.String(allow_none=True)
    profile_url = fields.String(allow_none=True)


class MovieDetailSchema(Schema):
    tmdb_id = fields.Int()
    title = fields.String(allow_none=True)
    year = fields.String(allow_none=True)
    runtime = fields.Int(allow_none=True)
    genres = fields.List(fields.String())
    overview = fields.String(allow_none=True)
    rating = fields.Float(allow_none=True)
    poster_url = fields.String(allow_none=True)
    backdrop_url = fields.String(allow_none=True)
    cast = fields.List(fields.Nested(CastMemberSchema))
