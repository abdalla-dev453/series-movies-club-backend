def follow_to_dict(follow):
    return {
        "id": follow.id,
        "follower_id": follow.follower_id,
        "followee_id": follow.followee_id,
        "created_at": follow.created_at.isoformat(),
    }
