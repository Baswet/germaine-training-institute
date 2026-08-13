"""
Consistent JSON response envelope for every API endpoint (Step 5).

Success shape:
    {"success": true,  "data": {...}, "message": "..."}

Error shape:
    {"success": false, "data": null,  "message": "...", "errors": {...}}

`errors` is a dict of field -> list[str] for validation failures, or
omitted entirely for non-validation errors (not-found, conflict, etc.).
"""

from flask import jsonify


def success(data=None, message: str = "Request completed successfully", status: int = 200):
    return jsonify({"success": True, "data": data, "message": message}), status


def error(message: str, status: int = 400, errors: dict | None = None):
    payload = {"success": False, "data": None, "message": message}
    if errors:
        payload["errors"] = errors
    return jsonify(payload), status
