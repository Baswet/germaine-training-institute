"""
READ-ONLY pre-deployment check for the Applicant Leads feature.

Run on the cPanel server from the backend root, inside the app's venv:

    cd /home2/germaine/germaine-backend
    source /home2/germaine/virtualenv/germaine-backend/3.12/bin/activate
    python scripts/predeploy_check_leads.py

(or via cPanel -> Setup Python App -> "Execute python script").

It changes nothing: no writes, no migrations, no restarts. It never prints
environment variable values, SECRET_KEY, or DATABASE_URL. Output:
  1. Python version.
  2. Alembic heads found in migrations/versions (file-based, no DB needed).
     Before deploying, set `down_revision` in
     migrations/versions/c4d9e2a7b1f0_applicant_leads.py to the single head
     printed here.
  3. Current database revision + whether applicant_leads already exists
     (read-only SELECTs).
  4. Whether each live file still contains the anchor text that the
     deployment guide tells you to edit next to.
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

print("== Applicant Leads pre-deploy check (read-only) ==")
print("Python:", sys.version.split()[0])
print("Backend root:", ROOT)

# ---- 2. migration heads from files only
try:
    from alembic.config import Config
    from alembic.script import ScriptDirectory
    cfg = Config()
    cfg.set_main_option("script_location", str(ROOT / "migrations"))
    script = ScriptDirectory.from_config(cfg)
    heads = script.get_heads()
    print("Alembic heads in migrations/versions:", heads)
    if "c4d9e2a7b1f0" in heads or any(r.revision == "c4d9e2a7b1f0" for r in script.walk_revisions()):
        print("  NOTE: lead migration c4d9e2a7b1f0 is already present in this folder.")
    if len(heads) > 1:
        print("  WARNING: more than one head. Resolve before adding a new migration.")
except Exception as exc:  # noqa: BLE001
    print("Could not read migration heads:", type(exc).__name__)

# ---- 3. DB revision (read-only)
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
    from app import create_app
    from app.extensions import db
    app = create_app()
    with app.app_context():
        with db.engine.connect() as conn:
            rev = conn.execute(db.text("SELECT version_num FROM alembic_version")).fetchall()
            print("Database alembic_version:", [r[0] for r in rev])
            exists = conn.execute(db.text(
                "SELECT to_regclass('public.applicant_leads') IS NOT NULL")).scalar()
            print("applicant_leads table exists:", bool(exists))
except Exception as exc:  # noqa: BLE001
    print("Database check skipped/failed:", type(exc).__name__)  # message omitted on purpose (may contain URL)

# ---- 4. anchors used by the deployment guide
ANCHORS = {
    "app/blueprints/admissions/routes.py": [
        "application = application_service.create_application(payload)",
        "@admissions_bp.route(\"/applications\", methods=[\"POST\"])",
    ],
    "app/blueprints/admin/__init__.py": ["admin_bp = Blueprint("],
    "app/models/__init__.py": ["__all__ = ["],
    "app/templates/admin/base.html": ["admin.scholarships_list"],
}
for rel, needles in ANCHORS.items():
    path = ROOT / rel
    if not path.exists():
        print(f"[MISSING] {rel}")
        continue
    text = path.read_text(encoding="utf-8", errors="replace")
    for n in needles:
        print(f"[{'ok' if n in text else 'NOT FOUND'}] {rel}: {n[:60]}")
    if "lead_service" in text or "lead_routes" in text or "ApplicantLead" in text:
        print(f"  NOTE: {rel} already references the lead feature.")
print("== done; nothing was changed ==")
