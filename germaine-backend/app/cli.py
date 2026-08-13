"""
Custom Flask CLI commands (Step 7, extended Phase 15).

`flask create-admin` is the only supported way to create the first (or
any) AdminUser row (Germaine's staff admin portal at /admin/, session-
cookie authenticated). It always prompts interactively for the password
(never accepts it as a plaintext command-line argument, so it can't
end up in shell history or process listings) and hashes it before
writing anything to the database. No admin credentials are hardcoded
anywhere in this codebase.

`flask create-earncash-admin` is the equivalent command for EarnCash's
entirely separate admin surface (earncash_users.role='admin', JWT
authenticated, used by build10/EarnCash/frontend/pages/admin-login.html
+ admin.html). Before Phase 15 there was no supported way to create
this account at all — EarnCash's public /auth/register endpoint always
creates role='user' by design, so the only way to get an admin account
was direct database manipulation. This command fills that real gap
using the same "always prompt, never accept a plaintext CLI/db value,
hash before storing" pattern as create-admin, reusing EarnCash's own
referral-code generator and password hashing scheme (Werkzeug PBKDF2-
SHA256 — identical algorithm to app/utils/security.hash_password, just
called directly here since EarnCash's own auth_routes.py already uses
werkzeug.security.generate_password_hash rather than that wrapper).
"""

import click
from flask import Flask

from app.extensions import db
from app.utils.security import hash_password


def register_cli(app: Flask) -> None:
    app.cli.add_command(create_admin)
    app.cli.add_command(create_earncash_admin)


@click.command("create-admin")
@click.option("--name", prompt="Admin full name", help="Display name for the admin account.")
@click.option("--email", prompt="Admin email", help="Login email — must be unique.")
@click.password_option(help="Login password (prompted, never passed as plaintext CLI args).")
def create_admin(name, email, password):
    """Create a new admin_users row with a securely hashed password."""
    from app.models import AdminUser

    email = email.strip().lower()
    existing = AdminUser.query.filter_by(email=email).first()
    if existing is not None:
        click.echo(f"An admin with email '{email}' already exists (id={existing.id}). Nothing changed.")
        return

    admin = AdminUser(name=name.strip(), email=email, password_hash=hash_password(password), is_active=True)
    db.session.add(admin)
    db.session.commit()
    click.echo(f"Created admin user '{admin.name}' <{admin.email}> (id={admin.id}).")


@click.command("create-earncash-admin")
@click.option("--name", prompt="EarnCash admin full name", help="Display name for the EarnCash admin account.")
@click.option("--email", prompt="EarnCash admin email", help="Login email — must be unique across earncash_users.")
@click.password_option(help="Login password (prompted, never passed as plaintext CLI args). Minimum 8 characters.")
def create_earncash_admin(name, email, password):
    """Create an earncash_users row with role='admin' and a securely hashed password.

    This is the ONLY supported way to create an EarnCash admin account.
    Registering through the public EarnCash sign-up form always creates
    a role='user' account by design (see auth_routes.py::register) —
    there is deliberately no way to self-elevate to admin through the
    API, so this account must be created here, on the server, by
    whoever controls deployment.
    """
    from app.models import EarnCashUser
    from app.utils.earncash_helpers import generate_referral_code, is_valid_email, is_valid_password

    email = email.strip().lower()

    if not is_valid_email(email):
        click.echo(f"'{email}' is not a valid email address. Nothing changed.")
        return
    if not is_valid_password(password):
        click.echo("Password must be at least 8 characters. Nothing changed.")
        return

    existing = EarnCashUser.query.filter_by(email=email).first()
    if existing is not None:
        if existing.role == "admin":
            click.echo(f"An EarnCash admin with email '{email}' already exists (id={existing.id}). Nothing changed.")
        else:
            click.echo(
                f"An EarnCash account with email '{email}' already exists as a regular user (id={existing.id}). "
                "Refusing to silently promote an existing user account to admin — if that's really what you "
                "want, do it deliberately via a direct, audited database update, not this command."
            )
        return

    new_code = generate_referral_code()
    while EarnCashUser.query.filter_by(referral_code=new_code).first():
        new_code = generate_referral_code()

    admin = EarnCashUser(
        fullname=name.strip(),
        email=email,
        password_hash=hash_password(password),
        referral_code=new_code,
        role="admin",
        status="active",
    )
    db.session.add(admin)
    db.session.commit()
    click.echo(f"Created EarnCash admin '{admin.fullname}' <{admin.email}> (id={admin.id}).")
    click.echo("Log in at the EarnCash admin login page (build10/EarnCash/frontend/pages/admin-login.html) with this email and password.")
