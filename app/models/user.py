from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, nullable=False, unique=True)
    email = db.Column(db.String(120), index=True, nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    bio = db.Column(db.String(255), nullable=True)
    avatar_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


    # relationships
    posts = db.relationship(
        "Post", backref="author", cascade="all, delete-orphan", passive_deletes=True
    )
    reviews = db.relationship(
        "Review", backref="author", cascade="all, delete-orphan", passive_deletes=True
    )
    watched_movies = db.relationship(
        "WatchedMovie",
        backref="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    club_memberships = db.relationship(
        "ClubMembership",
        backref="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    following = db.relationship(
        "Follow",
        foreign_keys="Follow.follower_id",
        backref="follower",
        passive_deletes=True,
        cascade="all, delete-orphan",
    )
    followers = db.relationship(
        "Follow",
        foreign_keys="Follow.followee_id",
        backref="followee",
        passive_deletes=True,
        cascade="all, delete-orphan",
    )

# password hashing
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"