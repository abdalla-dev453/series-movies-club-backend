"""Serialization for User.

Public user data is safe to expose to visitors.
Private user data is only returned for the authenticated user.
"""


def user_to_public_dict(user):
    """Serialize a user with information safe for public viewing."""
    return {
        "id": user.id,
        "username": user.username,
        "bio": user.bio,
        "avatar_url": user.avatar_url,
        "follower_count": len(user.followers),
        "following_count": len(user.following),
    }


def user_to_private_dict(user):
    """Serialize the authenticated user's full profile."""
    data = user_to_public_dict(user)

    data["email"] = user.email
    data["is_superuser"] = user.is_superuser
    data["is_banned"] = user.is_banned
    data["created_at"] = user.created_at.isoformat()

    return data


def serialize_user(user):
    """Backward-compatible public user serializer."""
    return user_to_public_dict(user)
