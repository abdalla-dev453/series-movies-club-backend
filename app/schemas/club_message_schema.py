from app.utils.error_handlers import APIError


def club_message_to_dict(message):
    return {
        "id": message.id,
        "club_id": message.club_id,
        "user_id": message.user_id,
        "username": message.user.username if message.user else None,
        "message": message.message,
        "created_at": message.created_at.isoformat(),
    }


def validate_club_message_payload(data):
    if not isinstance(data, dict):
        raise APIError("Request body must be a JSON object", 400)

    message = data.get("message")
    if message is None:
        raise APIError("message is required", 400)

    text = str(message).strip()
    if not text:
        raise APIError("message cannot be empty", 400)

    if len(text) > 2000:
        raise APIError("message is too long", 400)

    return {"message": text}
