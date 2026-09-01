from flask import Blueprint, jsonify
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    jwt_required,
)

from app.extensions import db
from app.models import TokenBlocklist, User
from app.schemas.user_schema import user_to_private_dict
from app.utils.error_handlers import APIError
from app.utils.time import utcnow
from app.utils.validators import get_json_body, require_fields, validate_signup_payload

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/signup")
def signup():
    data = get_json_body()
    username, email, password = validate_signup_payload(data)

    if User.query.filter_by(username=username).first() is not None:
        raise APIError("Username already taken", 409)
    if User.query.filter_by(email=email).first() is not None:
        raise APIError("Email already registered", 409)

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=str(user.id))
    return jsonify({"user": user_to_private_dict(user), "access_token": access_token}), 201


@auth_bp.post("/login")
def login():
    data = get_json_body()
    require_fields(data, "username", "password")

    user = User.query.filter_by(username=data["username"]).first()
    if user is None or not user.check_password(data["password"]):
        raise APIError("Invalid username or password", 401)

    access_token = create_access_token(identity=str(user.id))
    return jsonify({"user": user_to_private_dict(user), "access_token": access_token}), 200


@auth_bp.post("/logout")
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    db.session.add(TokenBlocklist(jti=jti, created_at=utcnow()))
    db.session.commit()
    return jsonify({"message": "Successfully logged out"}), 200
