"""Live smoke test after the Passenger restart. Read-only (GETs, plus one
POST to an unknown story slug that must 404). Writes no data."""
import json, urllib.error, urllib.request
from datetime import datetime
from pathlib import Path
API = "https://api.germaineinstitute.ac.ke"
SITE = "https://germaineinstitute.ac.ke"
LOG = Path.home() / "_claude_backups" / "newsroom_deploy_log.txt"
out = []


def req(url, method="GET", body=None):
    r = urllib.request.Request(url, data=body, method=method, headers={"Content-Type": "application/json", "User-Agent": "gti-smoke"})
    try:
        with urllib.request.urlopen(r, timeout=25) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


def check(name, ok, detail=""):
    out.append(f"SMOKE {'PASS' if ok else 'FAIL'} {name} {detail}")
    print(out[-1])


s, b = req(API + "/api/newsroom/home")
d = json.loads(b).get("data", {}) if s == 200 else {}
check("home 200", s == 200, s)
check("home has lead + events", bool(d.get("lead")) and bool(d.get("events", {}).get("upcoming")),
      f"latest={len(d.get('latest', []))} upcoming={len(d.get('events', {}).get('upcoming', []))}")
check("no breaking/most-read invented", d.get("breaking") == [] and d.get("most_read") == [])
s, b = req(API + "/api/newsroom/stories?category=sports"); check("stories filter", s == 200, s)
s, b = req(API + "/api/newsroom/stories?category=politics"); check("politics rejected", s == 422, s)
s, b = req(API + "/api/newsroom/events/wfcp-world-congress-2026"); check("event detail", s == 200, s)
s, b = req(API + "/api/newsroom/stories/does-not-exist-xyz/view", "POST", b"{}"); check("view unknown 404", s == 404, s)
s, b = req(API + "/admin/newsroom"); check("admin requires login", s in (200, 302, 401) and "New Story" not in b, s)
s, b = req(API + "/api/news"); check("existing /api/news ok", s == 200, s)
s, b = req(API + "/api/admissions/applications", "POST", b"{}"); check("applications validates", s == 422, s)
for page in ("news.html", "news-article.html", "event.html", "apply.html", "letter-render.html",
             "assets/js/newsroom.js", "assets/css/newsroom.css", "assets/js/bursary-letter.js"):
    s, b = req(SITE + "/" + page + "?smoke=" + datetime.now().strftime("%H%M%S")); check(page, s == 200, s)
s, b = req(SITE + "/apply.html"); check("apply loads bursary-letter.js", "bursary-letter.js" in b)
s, b = req(SITE + "/news.html"); check("news has newsroom.js", "newsroom.js" in b and "news-cms-bridge" not in b)
with open(LOG, "a", encoding="utf-8") as fh:
    fh.write("\n".join(out) + "\n\n")
print("SMOKE DONE", sum("FAIL" in x for x in out), "failures")
