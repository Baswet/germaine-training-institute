"""
Live HTTP smoke test for the Applicant Leads deploy, run on the server after
the Passenger restart. Goes through the real public URLs. Creates NO data:
the only POST is an empty body, which the API rejects with 422.
"""

import json
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

API = "https://api.germaineinstitute.ac.ke"
SITE = "https://germaineinstitute.ac.ke"
LOG = Path.home() / "_claude_backups" / "leads_deploy_log.txt"
out = []


def req(url, method="GET", body=None, headers=None):
    r = urllib.request.Request(url, data=body, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(r, timeout=20) as resp:
            return resp.status, dict(resp.headers), resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read().decode("utf-8", "replace")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def log(msg):
    out.append(f"{datetime.now().isoformat(timespec='seconds')} LIVE {msg}")
    print(out[-1])


ok = True
s, h, b = req(API + "/api/health")
log(f"GET /api/health -> {s}"); ok &= s == 200
s, h, b = req(API + "/api/admissions/leads/capture", "POST", b"{}",
              {"Content-Type": "application/json", "Origin": SITE})
cors = h.get("Access-Control-Allow-Origin")
log(f"POST /leads/capture {{}} -> {s} (expect 422); CORS allow-origin={cors}")
ok &= s == 422 and cors == SITE
opener = urllib.request.build_opener(NoRedirect)
try:
    opener.open(API + "/admin/leads", timeout=20)
    s = 200
except urllib.error.HTTPError as e:
    s = e.code
log(f"GET /admin/leads unauthenticated -> {s} (expect 302)"); ok &= s == 302
s, h, b = req(SITE + "/apply.html")
log(f"GET apply.html -> {s}; notice={'apLeadNotice' in b}; script={'lead-capture.js' in b}")
ok &= s == 200 and "apLeadNotice" in b and "lead-capture.js" in b
s, h, b = req(SITE + "/assets/js/lead-capture.js")
log(f"GET lead-capture.js -> {s}; size={len(b)}"); ok &= s == 200 and "GTILeadCapture" in b
s, h, b = req(SITE + "/assets/js/apply-wizard.js")
log(f"GET apply-wizard.js -> {s}; hooks={b.count('GTILeadCapture')}"); ok &= s == 200 and b.count("GTILeadCapture") >= 2
log("RESULT: OK" if ok else "RESULT: CHECK")
with open(LOG, "a", encoding="utf-8") as fh:
    fh.write("\n".join(out) + "\n\n")
