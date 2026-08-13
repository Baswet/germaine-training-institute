"""
Shared pytest fixtures.

Every test in this suite uses the "testing" config (app/config.py ->
TestingConfig), which points at an in-memory SQLite URI. No live
PostgreSQL server is required to run this suite, ever.

Two tiers of fixtures:

  - `app` / `client` — no tables are created. Used by tests that only
    check app construction, config, routing, and error-handler wiring
    (unchanged since Step 3).

  - `db_app` / `db_client` (Step 5, new) — creates all 15 tables against
    a fresh in-memory SQLite database for the duration of a single test
    function via db.create_all(), and tears them down again with
    db.drop_all() when the test ends. This is the standard, expected
    way to test service-layer query/relationship/transaction logic
    without a live database — it never touches the real PostgreSQL
    instance used in Step 4, and nothing here runs outside pytest.
"""

import pytest

from app import create_app
from app.extensions import db as _db


@pytest.fixture()
def app():
    app = create_app("testing")
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db_app():
    app = create_app("testing")
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def db_client(db_app):
    return db_app.test_client()
