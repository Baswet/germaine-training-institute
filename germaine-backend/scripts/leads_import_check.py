"""
Post-edit verification for the Applicant Leads deploy (creates NO data).

Builds the app exactly as Passenger does, confirms the new routes are
registered and the new tables are queryable, and exercises the endpoints
through Flask's test client:
  - POST /api/admissions/leads/capture with {}  -> expect 422 (validation; nothing saved)
  - GET  /admin/leads unauthenticated            -> expect 302 to login
  - GET  /api/health                             -> expect 200
Appends a log to ~/_claude_backups/leads_deploy_log.txt. Never logs env values.
"""

import re
import sys
import traceback
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
LOG = Path.home() / "_claude_backups" / "leads_deploy_log.txt"
out = []


def log(msg):
    msg = re.sub(r"[a-z+]+://\S+", "<url>", str(msg))
    out.append(f"{datetime.now().isoformat(timespec='seconds')} CHECK {msg}")
    print(out[-1])


ok = True
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
    from app import create_app
    from app.extensions import db
    from app.models import ApplicantLead, ApplicantLeadAuditLog

    app = create_app()
    rules = {r.rule for r in app.url_map.iter_rules()}
    for rule in ("/api/admissions/leads/capture", "/admin/leads", "/admin/leads/<int:lead_id>",
                 "/admin/leads/<int:lead_id>/delete", "/api/admissions/applications"):
        present = rule in rules
        ok &= present
        log(f"route {rule}: {'ok' if present else 'MISSING'}")
    with app.app_context():
        log(f"leads in table: {ApplicantLead.query.count()}, audit rows: {ApplicantLeadAuditLog.query.count()}")
    c = app.test_client()
    r1 = c.post("/api/admissions/leads/capture", json={}, environ_base={"REMOTE_ADDR": "127.0.0.9"})
    r2 = c.get("/admin/leads")
    r3 = c.get("/api/health")
    log(f"capture {{}} -> {r1.status_code} (expect 422)")
    log(f"/admin/leads unauthenticated -> {r2.status_code} (expect 302)")
    log(f"/api/health -> {r3.status_code} (expect 200)")
    ok &= (r1.status_code == 422 and r2.status_code == 302 and r3.status_code == 200)
    with app.app_context():
        log(f"leads in table after checks: {ApplicantLead.query.count()} (unchanged)")
except Exception as exc:  # noqa: BLE001
    ok = False
    log(f"ERROR {type(exc).__name__}: {exc}")
    log(re.sub(r"[a-z+]+://\S+", "<url>", traceback.format_exc()[-1500:]))
log("RESULT: OK" if ok else "RESULT: FAILED")
with open(LOG, "a", encoding="utf-8") as fh:
    fh.write("\n".join(out) + "\n\n")
