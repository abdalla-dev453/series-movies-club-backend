from datetime import datetime

from app.extensions import db


class Review(db.Model):
    """Rating + comment on a single post. One review per (post, user)."""

    __tablename__ = "reviews"
    __table_args__ = (
        db.UniqueConstraint("post_id", "user_id",
                            name="uq_review_per_user_post"),
    )

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(
        db.Integer, db.ForeignKey("posts.id", ondelete="CASCADE"), nullable=False
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment_text = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=True,
                           onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Review post={self.post_id} user={self.user_id} rating={self.rating}>"
