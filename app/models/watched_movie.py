from datetime import datetime

from app.extensions import db


class WatchedMovie(db.Model):
    """Personal watch log -- everything a user has watched, kept separate
    from Post since users track more than they choose to share."""

    __tablename__ = "watched_movies"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    movie_title = db.Column(db.String(255), nullable=False)
    poster_url = db.Column(db.String(500), nullable=True)
    watched_date = db.Column(db.Date, nullable=True)
    personal_rating = db.Column(db.Integer, nullable=True)  # 1-5
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<WatchedMovie {self.movie_title!r} user={self.user_id}>"
