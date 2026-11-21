"""
One-off deploy step for the Applicant Leads feature (run via cPanel
"Execute python script" or `python scripts/leads_deploy_migrate.py`).

1. Backs up the database with pg_dump (custom format) into
   ~/_claude_backups/. If pg_dump is not installed it logs that and continues,
   because the migration below is additive only (two new tables).
2. Runs `flask db upgrade` (Flask-Migrate) to head c4d9e2a7b1f0. It refuses
   unless the current DB revision is the expected live head e5f2a9c1d7b3 (or
   already c4d9e2a7b1f0).
3. Writes a log to ~/_claude_backups/leads_deploy_log.txt.

Never logs DATABASE_URL, SECRET_KEY or any env value: error messages are
scrubbed of anything URL-like.
"""

import os
import re
import shutil
import subprocess
import sys
import traceback
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
BACKUPS = Path.home() / "_claude_backups"
BACKUPS.mkdir(exist_ok=True)
LOG = BACKUPS / "leads_deploy_log.txt"
EXPECTED_PREVIOUS = "e5f2a9c1d7b3"
TARGET = "c4d9e2a7b1f0"
lines = []


def log(msg):
    msg = re.sub(r"[a-z+]+://\S+", "<url>", str(msg))
    msg = re.sub(r"(password|secret)[^\s,;]*\s*[=:]\s*\S+", r"\1=<redacted>", msg, flags=re.I)
    lines.append(f"{datetime.now().isoformat(timespec='seconds')} {msg}")
    print(lines[-1])


def flush():
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n\n")


try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
    from app import create_app
    from app.extensions import db
    from flask_migrate import upgrade

    app = create_app()
    with app.app_context():
        current = [r[0] for r in db.session.execute(db.text("SELECT version_num FROM alembic_version"))]
        log(f"DB revision before: {current}")
        if current not in ([EXPECTED_PREVIOUS], [TARGET]):
            log("ABORT: unexpected DB revision; nothing changed.")
            raise SystemExit(2)

        if current == [EXPECTED_PREVIOUS]:
            # ---- backup
            pg_dump = shutil.which("pg_dump")
            if pg_dump:
                url = os.environ.get("DATABASE_URL", "").replace("postgresql+psycopg://", "postgresql://")
                out = BACKUPS / f"gti-db-before-leads-{datetime.now():%Y%m%d-%H%M%S}.dump"
                p = subprocess.run([pg_dump, "-Fc", "-f", str(out), url], capture_output=True, text=True, timeout=600)
                if p.returncode == 0:
                    log(f"DB backup OK: {out.name} ({out.stat().st_size} bytes)")
                else:
                    log(f"ABORT: pg_dump failed (code {p.returncode}); nothing changed. {p.stderr[-300:]}")
                    raise SystemExit(3)
            else:
                log("pg_dump not available on this host; continuing (migration is additive only).")

            # ---- migrate
            db.session.remove()
            upgrade(directory=str(ROOT / "migrations"))
            db.session.remove()

        after = [r[0] for r in db.session.execute(db.text("SELECT version_num FROM alembic_version"))]
        tables = [r[0] for r in db.session.execute(db.text(
            "SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename LIKE 'applicant_lead%' ORDER BY 1"))]
        log(f"DB revision after: {after}; new tables: {tables}")
        log("RESULT: OK" if after == [TARGET] and len(tables) == 2 else "RESULT: CHECK MANUALLY")
except SystemExit:
    pass
except Exception as exc:  # noqa: BLE001
    log(f"ERROR {type(exc).__name__}: {exc}")
    log(traceback.format_exc()[-1500:])
finally:
    flush()
