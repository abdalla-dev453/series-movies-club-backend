import re

EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_user_payload(data):
    if not isinstance(data, dict):
        raise ValueError("User payload must be a dictionary.")
    username = str(data.get("username", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    if not username or len(username) < 3 or len(username) > 64:
        raise ValueError("Username must be 3-64 characters.")
    if not EMAIL.match(email):
        raise ValueError("Email is invalid.")
    if len(password) < 8 or len(password) > 128:
        raise ValueError("Password must be 8-128 characters.")
    bio = data.get("bio")
    if bio is not None and len(str(bio).strip()) > 255:
        raise ValueError("Bio cannot exceed 255 characters.")
    avatar = data.get("avatar_url")
    if avatar is not None and len(str(avatar).strip()) > 255:
        raise ValueError("Avatar URL cannot exceed 255 characters.")
    return {"username": username, "email": email, "password": password, "bio": bio, "avatar_url": avatar}


def validate_user_update_payload(data):
    if not isinstance(data, dict) or not data:
        raise ValueError("User update payload must be a non-empty dictionary.")
    allowed = {"username", "email", "password", "bio", "avatar_url"}
    if set(data) - allowed:
        raise ValueError("Invalid user fields provided.")
    return validate_user_payload({**{"username": "", "email": "", "password": ""}, **data})

    