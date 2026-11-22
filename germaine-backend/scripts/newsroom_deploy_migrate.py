"""
One-off deploy step for News & Events (run via cPanel "Execute python script").

1. pg_dump backup into ~/_claude_backups/ (aborts if pg_dump exists and fails).
2. flask db upgrade to e7a3b5c9d1f2 (two new additive tables). Refuses unless
   the current revision is c4d9e2a7b1f0 (or already e7a3b5c9d1f2).
3. Seeds the launch stories/events (idempotent; existing rows untouched).
Log: ~/_claude_backups/newsroom_deploy_log.txt. Never logs env values.
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
LOG = BACKUPS / "newsroom_deploy_log.txt"
EXPECTED_PREVIOUS = ("c4d9e2a7b1f0",)
TARGET = "e7a3b5c9d1f2"
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
        if not (len(current) == 1 and (current[0] in EXPECTED_PREVIOUS or current[0] == TARGET)):
            log("ABORT: unexpected DB revision; nothing changed.")
            raise SystemExit(2)

        if current[0] in EXPECTED_PREVIOUS:
            # ---- backup
            pg_dump = shutil.which("pg_dump")
            if pg_dump:
                url = os.environ.get("DATABASE_URL", "").replace("postgresql+psycopg://", "postgresql://")
                out = BACKUPS / f"gti-db-before-newsroom-{datetime.now():%Y%m%d-%H%M%S}.dump"
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
            upgrade(directory=str(ROOT / "migrations"), revision=TARGET)
            db.session.remove()

        after = [r[0] for r in db.session.execute(db.text("SELECT version_num FROM alembic_version"))]
        tables = [r[0] for r in db.session.execute(db.text(
            "SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename IN ('news_article_meta','news_events') ORDER BY 1"))]
        log(f"DB revision after: {after}; new tables: {tables}")
        if after == [TARGET] and len(tables) == 2:
            from app.services import newsroom_seed
            log(f"Seed: {newsroom_seed.seed()}")
            n_meta = db.session.execute(db.text("SELECT COUNT(*) FROM news_article_meta")).scalar()
            n_ev = db.session.execute(db.text("SELECT COUNT(*) FROM news_events WHERE publication_status='published'")).scalar()
            log(f"Rows: news_article_meta={n_meta} published_events={n_ev}")
            log("RESULT: OK")
        else:
            log("RESULT: CHECK MANUALLY")
except SystemExit:
    pass
except Exception as exc:  # noqa: BLE001
    log(f"ERROR {type(exc).__name__}: {exc}")
    log(traceback.format_exc()[-1500:])
finally:
    flush()
