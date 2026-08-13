"""Verifies the application factory produces a valid, correctly configured Flask app."""

from flask import Flask


def test_create_app_returns_flask_instance(app):
    assert isinstance(app, Flask)


def test_app_has_expected_blueprints_registered(app):
    registered = set(app.blueprints.keys())
    assert {"public", "admissions", "alumni", "enquiries", "admin"} <= registered


def test_app_error_handlers_registered(app):
    # Flask keys error_handler_spec by the HTTPException *class* for each
    # status code, not by the int itself — resolve via werkzeug's own
    # code->exception-class mapping rather than assuming int keys.
    from werkzeug.exceptions import default_exceptions

    handlers = app.error_handler_spec.get(None, {})
    registered_exception_classes = set()
    for status_map in handlers.values():
        registered_exception_classes.update(status_map.keys())

    for code in (400, 404, 409, 500):
        assert default_exceptions[code] in registered_exception_classes


def test_404_response_has_consistent_json_error_shape(client):
    response = client.get("/api/this-route-does-not-exist")
    assert response.status_code == 404

    data = response.get_json()
    # Step 5: every error response, including generic HTTP errors, uses
    # the same {success, data, message} envelope as every other endpoint.
    assert data["success"] is False
    assert data["data"] is None
    assert "message" in data
