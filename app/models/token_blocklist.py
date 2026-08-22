from app.extensions import db
from app.utils.time import utcnow


class TokenBlocklist(db.Model):
    """Revoked JWT identifiers. Checked on every protected request so that
    /logout can actually invalidate an otherwise-stateless access token."""

    __tablename__ = "token_blocklist"

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True, unique=True)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    def __repr__(self):
        return f"<TokenBlocklist jti={self.jti}>"
