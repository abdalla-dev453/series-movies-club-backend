from flask import Flask, jsonify

from config import config_by_name
from app.extensions import bcrypt, cors, db, jwt, migrate


def create_app(config_name="development"):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    @app.get("/health")
    @app.get("/api/health")
    def health_check():
        return jsonify({"status": "healthy"}), 200

    _init_extensions(app)
    _ensure_legacy_sqlite_columns(app)
    _init_jwt_callbacks(app)

    from app.blueprints import register_blueprints
    register_blueprints(app)

    from app.utils.error_handlers import register_error_handlers
    register_error_handlers(app)

    return app


def _ensure_legacy_sqlite_columns(app):
    """Backfill legacy SQLite databases created before newer club/user fields existed."""
    if "sqlite" not in str(app.config.get("SQLALCHEMY_DATABASE_URI", "")):
        return

    with app.app_context():
        from sqlalchemy import inspect

        inspector = inspect(db.engine)
        if not inspector.has_table("clubs"):
            return

        columns = [row["name"] for row in inspector.get_columns("clubs")]
        if "background_url" in columns:
            return

        with db.engine.begin() as connection:
            connection.execute(
                db.text("ALTER TABLE clubs ADD COLUMN background_url VARCHAR(255)")
            )


def _init_extensions(app):
    db.init_app(app)
    from app import models  # noqa: F401 -- registers tables on db.metadata
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app)

    cors.init_app(app, resources={
        r"/api/*": {
            "origins": [
                "https://vercel.app",
                "http://localhost:5173",
                "http://localhost:3000"
            ],
            "allow_headers": ["Content-Type", "Authorization"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        }
    })


def _init_jwt_callbacks(app):
    """Wire flask-jwt-extended's hooks to our TokenBlocklist table, so a
    /logout'd access token is rejected on every subsequent request even
    though JWTs are otherwise stateless."""
    from app.models import TokenBlocklist

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        return db.session.query(TokenBlocklist.id).filter_by(jti=jti).first() is not None

    @jwt.revoked_token_loader
    def revoked_token_response(jwt_header, jwt_payload):
        return jsonify({"error": "Token has been revoked"}), 401

    @jwt.expired_token_loader
    def expired_token_response(jwt_header, jwt_payload):
        return jsonify({"error": "Token has expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_response(reason):
        return jsonify({"error": "Invalid token"}), 401

    @jwt.unauthorized_loader
    def missing_token_response(reason):
        return jsonify({"error": "Missing authorization token"}), 401
