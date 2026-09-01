"""Import every model so its table is registered on db.metadata before
`db.create_all()` / Alembic autogenerate run, and so relationship() string
references (e.g. "ClubMember") can resolve at mapper-configuration time.
"""

from app.models.user import User
from app.models.club import Club
from app.models.club_member import ClubMember
from app.models.follow import Follow
from app.models.post import Post
from app.models.review import Review
from app.models.watched_movie import WatchedMovie
from app.models.token_blocklist import TokenBlocklist

__all__ = [
    "User",
    "Club",
    "ClubMember",
    "Follow",
    "Post",
    "Review",
    "WatchedMovie",
    "TokenBlocklist",
]
