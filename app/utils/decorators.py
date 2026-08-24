from app.extensions import db
from app.utils.error_handlers import APIError


def get_or_404(model, object_id, message=None):
    instance = db.session.get(model, object_id)
    if instance is None:
        raise APIError(message or "Resource not found", 404)
    return instance