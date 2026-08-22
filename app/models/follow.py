from datetime import datetime

from app.extensions import db


class Follow(db.Model):
    """Self-referential join table powering follow/unfollow between users."""

    __tablename__ = "follows"
    __table_args__ = (
        db.UniqueConstraint("follower_id", "followee_id", name="uq_follow_pair"),
    )

    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    followee_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Follow {self.follower_id} -> {self.followee_id}>"