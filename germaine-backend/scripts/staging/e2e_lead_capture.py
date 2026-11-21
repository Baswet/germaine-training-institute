"""End-to-end browser test of lead capture against the LOCAL staging stack
(static build10 on :8080, Flask on :5000, throwaway Postgres gti_staging).
Never touches production."""
import json
import subprocess
import sys
import time

from playwright.sync_api import sync_playwright

BASE = "http://localhost:8080/apply.html"
BRIAN = f"brian{int(time.time())}@example.com"
PSQL = ["su", "postgres", "-c"]
results = []


def sql(q):
    out = subprocess.run(PSQL + [f"psql -h /tmp -p 5433 gti_staging -At -F '|' -c \"{q}\""],
                         capture_output=True, text=True)
    return out.stdout.strip()


def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))
    print(("PASS " if cond else "FAIL ") + name + (f" — {detail}" if detail else ""))


def server_posts():
    return open("/tmp/flask.log").read().count("POST /api/admissions/leads/capture")


sql("DELETE FROM applicant_leads")
sql("DELETE FROM applicant_lead_audit_logs")

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path="/usr/bin/google-chrome", headless=True)
    ctx = browser.new_context(viewport={"width": 390, "height": 844})  # mobile size
    page = ctx.new_page()
    errors, capture_calls = [], []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.on("request", lambda r: capture_calls.append(r.post_data) if "/leads/capture" in r.url else None)

    posts_before = server_posts()
    page.goto(BASE)
    page.wait_for_load_state("networkidle")
    check("privacy notice visible next to phone field", page.is_visible("#apLeadNotice"))

    # Test 6: invalid phone -> nothing saved
    page.type("#apFullname", "Achieng Otieno", delay=40)
    page.type("#apPhone", "12345", delay=40)
    time.sleep(2.5)
    check("T6 invalid phone not captured", sql("SELECT count(*) FROM applicant_leads") == "0")

    # Test 1 + 7: valid details typed keystroke by keystroke
    page.fill("#apPhone", "")
    page.type("#apPhone", "0712 345 678", delay=60)
    time.sleep(2.5)
    rows = sql("SELECT applicant_name, normalized_phone, lead_status FROM applicant_leads")
    check("T1 lead saved without submitting", rows == "Achieng Otieno|254712345678|new_lead", rows)
    n = server_posts() - posts_before
    check("T7 ~26 keystrokes debounced into 1-2 requests", 1 <= n <= 2, f"{n} POSTs")
    check("no lead data in browser-visible storage besides token",
          set(page.evaluate("Object.keys(localStorage)")) == {"gti_lead_token_v1"})

    # Test 2: continue filling -> same lead gets email, school, programme
    page.type("#apEmail", "achieng@example.com", delay=20)
    page.select_option("#apSchool", index=1)
    page.click("#apProgrammeSearch")
    page.wait_for_selector(".ap-combobox-item")
    prog = page.get_attribute(".ap-combobox-item", "data-name")
    page.dispatch_event(".ap-combobox-item", "mousedown")
    time.sleep(2.5)
    rows = sql("SELECT count(*), max(email), max(programme), max(school) FROM applicant_leads")
    check("T2 same lead updated with email/school/programme", rows.startswith("1|achieng@example.com|" + prog), rows)

    # Test 3: phone corrected
    page.fill("#apPhone", "")
    page.type("#apPhone", "722000111", delay=30)
    time.sleep(2.5)
    rows = sql("SELECT count(*), max(normalized_phone) FROM applicant_leads")
    check("T3 phone change updates existing lead", rows == "1|254722000111", rows)

    # Test 4: applicant leaves and comes back later (same browser)
    page.goto("about:blank")
    page = ctx.new_page()
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(BASE)
    page.wait_for_load_state("networkidle")
    page.type("#apFullname", "Achieng Atieno Otieno", delay=10)
    page.type("#apPhone", "722000111", delay=10)
    time.sleep(2.5)
    rows = sql("SELECT count(*), max(applicant_name) FROM applicant_leads")
    check("T4 revisit updates same lead (no duplicate)", rows == "1|Achieng Atieno Otieno", rows)

    # Test 5: complete and submit
    page.select_option("#apGender", "Female")
    page.select_option("#apCounty", "Kisumu")
    page.select_option("#apEduLevel", "KCSE")
    page.select_option("#apMode", "fulltime")
    page.select_option("#apSchool", index=1)
    page.click("#apProgrammeSearch")
    page.wait_for_selector(".ap-combobox-item")
    page.dispatch_event(".ap-combobox-item", "mousedown")
    page.fill("#apEmail", "achieng@example.com")
    page.check("#apTerms")
    page.click("#apSubmitBtn")
    page.wait_for_selector("#apSuccess.active", timeout=15000)
    time.sleep(1)
    rows = sql("SELECT l.lead_status, a.reference_code IS NOT NULL, l.first_captured_at < a.submitted_at "
               "FROM applicant_leads l JOIN applications a ON a.id = l.application_id")
    check("T5 submission links lead (status submitted, app linked)", rows == "application_submitted|t|t", rows)
    check("token cleared after successful submission",
          page.evaluate("localStorage.getItem('gti_lead_token_v1')") is None)
    check("still exactly one lead", sql("SELECT count(*) FROM applicant_leads") == "1")

    # Test 9: capture API down -> form still works, no error shown
    ctx2 = browser.new_context()
    page2 = ctx2.new_page()
    page2.route("**/leads/capture", lambda route: route.abort())
    page2.goto(BASE)
    page2.wait_for_load_state("networkidle")
    page2.type("#apFullname", "Brian Mwangi", delay=10)
    page2.type("#apPhone", "0733111222", delay=10)
    time.sleep(2.5)
    page2.select_option("#apGender", "Male")
    page2.select_option("#apCounty", "Nairobi")
    page2.select_option("#apEduLevel", "KCSE")
    page2.select_option("#apMode", "parttime")
    page2.select_option("#apSchool", index=1)
    page2.click("#apProgrammeSearch")
    page2.wait_for_selector(".ap-combobox-item")
    page2.dispatch_event(".ap-combobox-item", "mousedown")
    page2.fill("#apEmail", BRIAN)
    page2.check("#apTerms")
    visible_error = page2.is_visible("#apSubmitError.show")
    page2.click("#apSubmitBtn")
    page2.wait_for_selector("#apSuccess.active", timeout=15000)
    check("T9 capture API down: no error shown, application still submits",
          not visible_error and sql("SELECT count(*) FROM applications WHERE applicant_id IN "
                                    "(SELECT id FROM applicants WHERE email='" + BRIAN + "')") == "1")

    # Test 9b: capture endpoint returns 500 -> silent
    ctx3 = browser.new_context()
    page3 = ctx3.new_page()
    page3.route("**/leads/capture", lambda route: route.fulfill(status=503, body='{"success":false}',
                                                                 content_type="application/json"))
    page3.goto(BASE)
    page3.type("#apFullname", "Faith Chebet", delay=5)
    page3.type("#apPhone", "0700111222", delay=5)
    time.sleep(2.5)
    check("T9b server error is silent to applicant", not page3.is_visible("#apSubmitError.show"))

    page.screenshot(path="/home/claude/e2e/apply_mobile_after_submit.png", full_page=False)
    real_errors = [e for e in errors if "favicon" not in e and "Failed to load resource" not in e]
    check("no JS errors on apply page", not real_errors, "; ".join(real_errors[:3]))
    browser.close()

failed = [r for r in results if not r[1]]
print(f"\n{len(results) - len(failed)}/{len(results)} checks passed")
json.dump([{"check": n, "pass": ok, "detail": d} for n, ok, d in results],
          open("/home/claude/e2e/e2e_results.json", "w"), indent=1)
sys.exit(1 if failed else 0)
