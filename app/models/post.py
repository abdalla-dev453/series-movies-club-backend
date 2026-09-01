from app.extensions import db
from app.utils.time import utcnow


class Post(db.Model):
    """A 'watched & shared' entry. club_id is null for a personal-feed
    post, set when shared into a specific club."""

    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    club_id = db.Column(
        db.Integer, db.ForeignKey("clubs.id", ondelete="CASCADE"), nullable=True
    )
    movie_title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    tmdb_id = db.Column(db.Integer, nullable=True)


# relationships
    reviews = db.relationship(
        "Review", backref="post", passive_deletes=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Post {self.movie_title!r} by user={self.user_id}>"
