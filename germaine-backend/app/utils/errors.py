"""
Centralized error handlers.

Registered once, in the app factory, against the whole app so every
route — public, admissions, alumni, enquiries, admin — returns the same
consistent JSON envelope (app/utils/responses.py's `error()` shape):

    {"success": false, "data": null, "message": "...", "errors": {...}}

Stack traces and internal exception text are never included in a
response body; in DEBUG_ERRORS-enabled environments (local dev only) a
short `detail` field may be added to `message`, but production config
never sets that flag.

Step 5 note: prior to Step 5, generic HTTP errors (400/404/409/500) used
a different shape ({"error": {"code": ..., "message": ...}}). They now
use the same envelope as every other API response, for consistency
across the whole backend — this was a deliberate, documented change,
not an accidental deviation (see the Step 5 report).
"""

from flask import current_app

from app.utils.responses import error
from app.utils.validation import ValidationError, NotFoundError


def register_error_handlers(app):
    @app.errorhandler(ValidationError)
    def handle_validation_error(err: ValidationError):
        return error("Validation failed.", status=422, errors=err.errors)

    @app.errorhandler(NotFoundError)
    def handle_not_found_error(err: NotFoundError):
        return error(err.message, status=404)

    @app.errorhandler(400)
    def handle_400(err):
        return error(_detail("The request could not be understood.", err), status=400)

    @app.errorhandler(401)
    def handle_401(err):
        return error("Authentication is required for this request.", status=401)

    @app.errorhandler(403)
    def handle_403(err):
        return error("You do not have permission to perform this action.", status=403)

    @app.errorhandler(404)
    def handle_404(err):
        return error("The requested resource was not found.", status=404)

    @app.errorhandler(409)
    def handle_409(err):
        return error(_detail("The request conflicts with existing data.", err), status=409)

    @app.errorhandler(422)
    def handle_422(err):
        return error("The request was understood but could not be processed.", status=422)

    @app.errorhandler(500)
    def handle_500(err):
        # Never leak stack traces or exception internals to the client.
        app.logger.exception("Unhandled server error")
        return error("An unexpected error occurred.", status=500)


def _detail(message: str, err) -> str:
    if current_app.config.get("DEBUG_ERRORS"):
        return f"{message} ({err})"
    return message
