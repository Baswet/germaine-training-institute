"""
Shared, narrowly-scoped CORS handling for the "/api/..." surface — both
the public catalogue/enquiry API (Step 7 §22/§26) and the EarnCash
blueprint's JWT-authenticated routes.

Design decisions, made explicitly rather than defaulted:
  - No CORS headers are added anywhere by default. `CORS_ALLOWED_ORIGINS`
    (a comma-separated env var, empty by default) is the single opt-in
    switch — if it's unset, the API behaves exactly as it did before
    Step 7 (no cross-origin headers at all, i.e. same-origin only).
  - Only ever applied to "/api/..." routes — never to "/admin/...". The
    session-cookie-authenticated admin portal must never be reachable
    cross-origin; CORS is not enabled there under any configuration.
  - No `Access-Control-Allow-Credentials` header is ever sent — nothing
    under "/api/" relies on cookies/sessions. EarnCash's own auth is a
    bearer JWT sent via the Authorization header, not a cookie, so this
    remains true even though EarnCash routes are now covered here too.
  - No wildcard ("*") is used when an explicit origin list is
    configured; if the request's Origin isn't in the configured list,
    no CORS header is added for that response (the browser then blocks
    the cross-origin read, exactly as intended).
  - Allow-Methods/Allow-Headers cover every method/header actually used
    under "/api/": GET/POST for the public catalogue+enquiry endpoints,
    plus PUT/DELETE and the "Authorization" bearer-token header used by
    EarnCash's JWT-protected routes. "Content-Type" stays listed since
    every JSON POST/PUT body needs it. (Originally this list was
    GET/POST + Content-Type only, written before EarnCash existed —
    that omission silently broke every authenticated EarnCash request
    cross-origin, since browsers refuse to send a header the preflight
    response doesn't allow.)
"""

import os

from flask import request, Flask

ALLOWED_METHODS = "GET, POST, PUT, DELETE, OPTIONS"
ALLOWED_HEADERS = "Content-Type, Authorization"


def _configured_origins() -> list[str]:
    raw = os.environ.get("CORS_ALLOWED_ORIGINS", "")
    return [o.strip() for o in raw.split(",") if o.strip()]


def register_cors(app: Flask) -> None:
    allowed_origins = _configured_origins()
    if not allowed_origins:
        return  # opt-in only — nothing registered, no behavior change

    @app.after_request
    def add_cors_headers(response):
        if not request.path.startswith("/api/"):
            return response
        origin = request.headers.get("Origin")
        if origin and origin in allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Vary"] = "Origin"
            response.headers["Access-Control-Allow-Methods"] = ALLOWED_METHODS
            response.headers["Access-Control-Allow-Headers"] = ALLOWED_HEADERS
        return response
