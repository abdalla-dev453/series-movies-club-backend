from app.extensions import db
from app.utils.time import utcnow


class Club(db.Model):
    __tablename__ = "clubs"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    # Display-only "founded by" -- never a permission source (see ClubMember.role).
    # SET NULL so the club survives if the creator's account is deleted.
    created_by = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)


# relationships
    members = db.relationship(
        "ClubMember", backref="club", passive_deletes=True, cascade="all, delete-orphan"
    )
    posts = db.relationship(
        "Post", backref="club", passive_deletes=True, cascade="all, delete-orphan"
    )
    founder = db.relationship("User", foreign_keys=[created_by])

    def __repr__(self):
        return f"<Club {self.name}>"
