from app.schemas.user_schema import user_to_public_dict


def club_member_to_dict(member):
    return {
        "id": member.id,
        "club_id": member.club_id,
        "user_id": member.user_id,
        "role": member.role,
        "joined_at": member.joined_at.isoformat(),
        "user": user_to_public_dict(member.user),
    }
