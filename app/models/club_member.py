from datetime import datetime

from app.extensions import db


class ClubMember(db.Model):
    """Join table resolving the many-to-many between users and clubs.

    role is the single source of truth for club permissions -- never
    Club.created_by, which is historical/display-only.
    """

    __tablename__ = "club_members"
    __table_args__ = (
        db.UniqueConstraint("club_id", "user_id", name="uq_membership"),
    )

    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(
        db.Integer, db.ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role = db.Column(db.String(20), nullable=False, default="member")  # 'member' | 'admin'
    joined_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<ClubMember club={self.club_id} user={self.user_id} role={self.role}>"