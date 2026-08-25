from atexit import register

from flask import Flask, jsonify

from config import config_by_name
from app.extensions import bcrypt, cors, db, jwt, migrate


def create_app(config_name="development"):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    _init_extensions(app)
    _init_jwt_callbacks(app)

    from app.blueprints import register_blueprints

    register_blueprints(app)

    from app.utils.error_handlers import register_error_handlers
    register_error_handlers(app)

    return app


def _init_extensions(app):
    db.init_app(app)
    from app import models  # noqa: F401 -- registers tables on db.metadata
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app)


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
