"""Serialization for User. `to_public_dict` is what every other schema
embeds (e.g. a post's author) -- it never includes the email or password
hash, only what's safe to show to any visitor."""


def user_to_public_dict(user):
    return {
        "id": user.id,
        "username": user.username,
        "bio": user.bio,
        "avatar_url": user.avatar_url,
    }


def user_to_private_dict(user):
    """Includes account-only fields. Only ever return this for the
    authenticated user themselves (signup/login/"my profile")."""
    data = user_to_public_dict(user)
    data["email"] = user.email
    data["created_at"] = user.created_at.isoformat()
    return data


def serialize_user(user):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        # add other fields as needed
    }