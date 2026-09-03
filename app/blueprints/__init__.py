from app.blueprints.movies import movies_bp
from app.blueprints.auth import auth_bp
from app.blueprints.users import users_bp
from app.blueprints.reviews import reviews_bp
from app.blueprints.posts import posts_bp
from app.blueprints.clubs import clubs_bp
from app.blueprints.club_members import club_members_bp
from app.blueprints.club_messages import club_messages_bp
from app.blueprints.watched_movies import watched_movies_bp
from app.blueprints.admin import admin_bp


def register_blueprints(app):
    app.register_blueprint(
        movies_bp,
        url_prefix="/api/movies"
    )

    app.register_blueprint(
        auth_bp,
        url_prefix="/api/auth"
    )

    app.register_blueprint(
        users_bp,
        url_prefix="/api/users"
    )

    app.register_blueprint(
        reviews_bp,
        url_prefix="/api/reviews"
    )

    app.register_blueprint(
        posts_bp,
        url_prefix="/api/posts"
    )

    app.register_blueprint(
        clubs_bp,
        url_prefix="/api/clubs"
    )

    app.register_blueprint(
        club_members_bp,
        url_prefix="/api/clubs"
    )

    app.register_blueprint(
        club_messages_bp,
        url_prefix="/api/clubs"
    )

    app.register_blueprint(
        watched_movies_bp,
        url_prefix="/api/watched"
    )

    app.register_blueprint(admin_bp, url_prefix="/api/admin")
