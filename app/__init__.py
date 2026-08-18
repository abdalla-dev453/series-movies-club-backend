import os
from flask import Flask
from config import config
from app.extensions import db, migrate, jwt, bcrypt, cors


def create_app(config_name=None):
    config_name = config_name or os.environ.get("FLASK_ENV", "default")

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})

    # from app.models import user, club, club_member, post, review, follow, watched_movie  # noqa

    # from app.blueprints.auth import auth_bp
    # from app.blueprints.users import users_bp
    # from app.blueprints.clubs import clubs_bp
    # from app.blueprints.club_members import club_members_bp
    # from app.blueprints.posts import posts_bp
    # from app.blueprints.reviews import reviews_bp
    # from app.blueprints.follows import follows_bp
    # from app.blueprints.watched_movies import watched_movies_bp

    # app.register_blueprint(auth_bp, url_prefix="/api/auth")
    # app.register_blueprint(users_bp, url_prefix="/api/users")
    # app.register_blueprint(clubs_bp, url_prefix="/api/clubs")
    # app.register_blueprint(club_members_bp, url_prefix="/api/clubs")
    # app.register_blueprint(posts_bp, url_prefix="/api/posts")
    # app.register_blueprint(reviews_bp, url_prefix="/api/reviews")
    # app.register_blueprint(follows_bp, url_prefix="/api/follows")
    # app.register_blueprint(watched_movies_bp, url_prefix="/api/watched")

    # from app.utils.error_handlers import register_error_handlers
    # register_error_handlers(app)

    return app