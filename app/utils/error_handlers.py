"""Central place for API error handling.

Every route raises `APIError` for expected failure cases (bad input,
missing resource, permission denied, conflicts) instead of building
`jsonify(...), status` tuples inline. That keeps the error JSON shape
consistent everywhere: `{"error": "<message>"}`.
"""


from flask import jsonify

class APIError(Exception):
    """
    client-facing API failure
    """
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code  


def register_error_handlers(app):
    @app.errorhandler(APIError)
    def handle_api_error(error):
            return jsonify({"error": error.message}), error.status_code

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(500)
    def handle_internal_error(error):
        app.logger.exception(error)
        return jsonify({"error": "Server error"}), 500