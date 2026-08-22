"""Single source of truth for "now" in models, so every `default=` column
uses the same timezone-aware clock instead of the deprecated
`datetime.utcnow`."""

from datetime import datetime, timezone


def utcnow():
    return datetime.now(timezone.utc)
