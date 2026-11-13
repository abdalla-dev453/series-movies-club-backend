"""Serialization schemas for legal movie watch information."""
from marshmallow import Schema, fields, validate


class CountryQuerySchema(Schema):
    country = fields.String(validate=validate.Regexp(r"^[A-Z]{2}$"))


class VideoSchema(Schema):
    id = fields.String()
    name = fields.String()
    key = fields.String()
    site = fields.String()
    type = fields.String()
    official = fields.Boolean()
    published_at = fields.String(allow_none=True)


class PrimaryTrailerSchema(Schema):
    key = fields.String(allow_none=True)
    site = fields.String(allow_none=True)
    name = fields.String(allow_none=True)


class ProviderSchema(Schema):
    provider_id = fields.Integer()
    provider_name = fields.String()
    logo_path = fields.String(allow_none=True)
    deep_link = fields.String()


class WatchProvidersSchema(Schema):
    country_code = fields.String()
    stream = fields.List(fields.Nested(ProviderSchema))
    rent = fields.List(fields.Nested(ProviderSchema))
    buy = fields.List(fields.Nested(ProviderSchema))


class WatchResponseSchema(Schema):
    tmdb_id = fields.Integer()
    title = fields.String(allow_none=True)
    videos = fields.List(fields.Nested(VideoSchema))
    watch_providers = fields.Nested(WatchProvidersSchema)
    primary_trailer = fields.Nested(PrimaryTrailerSchema)
