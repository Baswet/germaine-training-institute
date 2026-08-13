"""
Tests for the custom `flask` CLI commands (app/cli.py) — Phase 15.

Neither `create-admin` nor `create-earncash-admin` had any automated
coverage before this file: they were exercised manually in past
sessions, but a regression here would not have been caught by `pytest`.
Both commands are the ONLY supported way to create their respective
admin account type (Germaine staff portal vs. EarnCash's own admin
surface — see app/cli.py's module docstring for why these are two
separate systems), so they are worth protecting explicitly.

Uses Click's CliRunner against the same in-memory SQLite db_app fixture
every other test in this suite uses — no live PostgreSQL required.
"""

from click.testing import CliRunner

from app.cli import create_admin, create_earncash_admin
from app.models import AdminUser, EarnCashUser
from app.utils.security import verify_password


def _invoke(app, command, args, password="TestPass123"):
    runner = CliRunner()
    with app.app_context():
        return runner.invoke(command, args, input=f"{password}\n{password}\n")


# ---------------------------------------------------------------
# flask create-admin
# ---------------------------------------------------------------

def test_create_admin_creates_row_with_hashed_password(db_app):
    result = _invoke(db_app, create_admin, ["--name", "Jane Admin", "--email", "jane@example.com"])
    assert result.exit_code == 0
    assert "Created admin user" in result.output

    with db_app.app_context():
        admin = AdminUser.query.filter_by(email="jane@example.com").first()
        assert admin is not None
        assert admin.name == "Jane Admin"
        assert admin.is_active is True
        # Never stored in plaintext.
        assert admin.password_hash != "TestPass123"
        assert verify_password("TestPass123", admin.password_hash)


def test_create_admin_refuses_duplicate_email(db_app):
    _invoke(db_app, create_admin, ["--name", "First", "--email", "dupe@example.com"])
    result = _invoke(db_app, create_admin, ["--name", "Second", "--email", "dupe@example.com"], password="OtherPass1")

    assert "already exists" in result.output
    with db_app.app_context():
        # Still only one row, and it's still the first admin's name.
        matches = AdminUser.query.filter_by(email="dupe@example.com").all()
        assert len(matches) == 1
        assert matches[0].name == "First"


def test_create_admin_email_is_lowercased(db_app):
    _invoke(db_app, create_admin, ["--name", "Case Test", "--email", "MixedCase@Example.com"])
    with db_app.app_context():
        assert AdminUser.query.filter_by(email="mixedcase@example.com").first() is not None


# ---------------------------------------------------------------
# flask create-earncash-admin  (Phase 15 addition — closes the
# previously-unresolved "EarnCash admin account gap")
# ---------------------------------------------------------------

def test_create_earncash_admin_creates_row_with_admin_role(db_app):
    result = _invoke(db_app, create_earncash_admin, ["--name", "EC Admin", "--email", "ecadmin@example.com"])
    assert result.exit_code == 0
    assert "Created EarnCash admin" in result.output

    with db_app.app_context():
        admin = EarnCashUser.query.filter_by(email="ecadmin@example.com").first()
        assert admin is not None
        assert admin.role == "admin"
        assert admin.status == "active"
        assert admin.referral_code  # still gets a valid unique code, same as regular users
        assert verify_password("TestPass123", admin.password_hash)


def test_create_earncash_admin_can_log_in_via_real_route(db_app):
    _invoke(db_app, create_earncash_admin, ["--name", "EC Admin", "--email", "ecadmin2@example.com"])
    client = db_app.test_client()
    resp = client.post(
        "/api/earncash/admin/login",
        json={"email": "ecadmin2@example.com", "password": "TestPass123"},
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["admin"]["role"] == "admin"
    assert "token" in body


def test_create_earncash_admin_refuses_duplicate_email(db_app):
    _invoke(db_app, create_earncash_admin, ["--name", "First", "--email", "dupe-ec@example.com"])
    result = _invoke(db_app, create_earncash_admin, ["--name", "Second", "--email", "dupe-ec@example.com"], password="OtherPass1")

    assert "already exists" in result.output
    with db_app.app_context():
        assert EarnCashUser.query.filter_by(email="dupe-ec@example.com").count() == 1


def test_create_earncash_admin_refuses_to_silently_promote_existing_user(db_app):
    """A regular EarnCash user who happens to share an email with an
    admin-creation attempt must NOT be silently upgraded to admin —
    that would be a privilege-escalation footgun. The operator must do
    that deliberately via a direct database action, not this command."""
    with db_app.app_context():
        from app.extensions import db
        from app.utils.earncash_helpers import generate_referral_code

        user = EarnCashUser(
            fullname="Regular User", email="regular@example.com",
            password_hash="irrelevant-hash", referral_code=generate_referral_code(),
            role="user", status="active",
        )
        db.session.add(user)
        db.session.commit()

    result = _invoke(db_app, create_earncash_admin, ["--name", "Attempted Promotion", "--email", "regular@example.com"])
    assert "Refusing to silently promote" in result.output

    with db_app.app_context():
        still_user = EarnCashUser.query.filter_by(email="regular@example.com").first()
        assert still_user.role == "user"


def test_create_earncash_admin_rejects_weak_password(db_app):
    result = _invoke(db_app, create_earncash_admin, ["--name", "Weak", "--email", "weak@example.com"], password="short")
    assert "at least 8 characters" in result.output
    with db_app.app_context():
        assert EarnCashUser.query.filter_by(email="weak@example.com").first() is None


def test_create_earncash_admin_rejects_invalid_email(db_app):
    result = _invoke(db_app, create_earncash_admin, ["--name", "Bad Email", "--email", "not-an-email"])
    assert "not a valid email" in result.output
    with db_app.app_context():
        assert EarnCashUser.query.count() == 0


def test_create_earncash_admin_does_not_grant_germaine_admin_portal_access(db_app):
    """Sanity check on the architecture boundary already covered
    elsewhere for the reverse direction (test_earncash.py) — an
    EarnCash admin account must have no row in admin_users at all, so
    it can never authenticate against /admin/login."""
    _invoke(db_app, create_earncash_admin, ["--name", "EC Only", "--email", "ec-only@example.com"])
    with db_app.app_context():
        assert AdminUser.query.filter_by(email="ec-only@example.com").first() is None
