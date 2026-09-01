from app.extensions import db
from app.utils.time import utcnow


class ClubMessage(db.Model):
    __tablename__ = "club_messages"

    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(
        db.Integer,
        db.ForeignKey("clubs.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    def __repr__(self):
        return f"<ClubMessage club={self.club_id} user={self.user_id}>"
