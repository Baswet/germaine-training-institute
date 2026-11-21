# Applicant Lead Capture — Implementation Report & Deployment Guide

**Status: implemented and tested in an isolated staging environment. NOT deployed.**
Production deployment needs your explicit approval and the pre-deployment steps in §12.

| | |
|---|---|
| Repository | `Baswet/germaine-training-institute` |
| Branch | `feature/applicant-lead-capture` (not `main` — pushing `build10/` to `main` triggers the GitHub Pages deploy) |
| Migration | `c4d9e2a7b1f0` (additive only — two new tables) |
| Tests | 295 pytest (214 existing + 81 new) · 5 PostgreSQL · 14/14 headless-browser E2E |

---

## 1. What was inspected

**GitHub repo (full):** `germaine-backend/` app factory, config, 28 models, `admissions` blueprint and `application_service.create_application`, admin blueprint (session auth `utils/auth.py`, CSRF `utils/csrf.py`), admin templates/CSS, 4 migrations (head `8b1f4c9d2e3a`), 17 test modules; `build10/apply.html`, `assets/js/apply-wizard.js`, `assets/js/api-client.js`.

**Live cPanel (read-only, via your Chrome session):**
- Setup Python App: Python **3.12.16**, app root `germaine-backend`, URL **api.germaineinstitute.ac.ke**, startup `passenger_wsgi.py`, entry point `application`.
- Environment variable **names only** (no values read): `CORS_ALLOWED_ORIGINS, DATABASE_URL, FLASK_APP, FLASK_ENV, SECRET_KEY, SMTP_FROM, SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USERNAME, SMTP_USE_SSL`.
- `/home2/germaine/germaine-backend` directory listing. `.env`, `.env.save`, `.envy` exist and were **not opened**.

### ⚠️ Key finding: the live backend has drifted from GitHub

| | GitHub `main` | Live server |
|---|---|---|
| Migrations | 4 (head `8b1f4c9d2e3a`) | **10** — adds `a1b2c3d4e5f6` alumni_profile_fields, `b7c1d9e4f2a8` application_study_mode_fee, `c4d7f9a1b2e6` earncash_referral_opens, `dd6cf06dc972` add_driving_school_programme_type, `e5f2a9c1d7b3` alumni_email_optional, `f3a9c7e21b04` add_admin_password_reset_token_fields |
| Files changed after 17 Aug | — | **63 files / ~355 KB**, incl. `admin/routes.py` (36 KB), `admin_service.py`, `application_service.py`, `admissions/routes.py`, new `document_service`, `notification_service`, `sms_service`, `whatsapp_service`, `excel_service`, many new admin templates |

**Consequences:**
1. Files from this branch must **not** be copied over the live versions of the 5 shared files. The deployment adds new files and applies small, marked hook edits to the live copies (§12).
2. The lead migration's `down_revision` must be set to the **live** head before it runs. Otherwise Alembic sees two heads and `flask db upgrade` stops.
3. GitHub is not currently an accurate record of production. Syncing the live source into GitHub was attempted and is still outstanding (§11).

## 2. Files added / modified (branch vs `main`)

**New**
- `germaine-backend/app/models/applicant_lead.py` — `ApplicantLead`, `ApplicantLeadAuditLog`
- `germaine-backend/migrations/versions/c4d9e2a7b1f0_applicant_leads.py`
- `germaine-backend/app/services/lead_service.py` — capture, linking, stats, list, follow-up, delete, anonymise
- `germaine-backend/app/utils/phone.py` — Kenyan phone normalization + masking
- `germaine-backend/app/utils/rate_limit.py` — in-process sliding-window limiter
- `germaine-backend/app/blueprints/admin/lead_routes.py`
- `germaine-backend/app/templates/admin/leads_list.html`, `lead_detail.html`, `lead_delete_confirm.html`
- `build10/assets/js/lead-capture.js`
- `germaine-backend/scripts/predeploy_check_leads.py` (read-only server check)
- `germaine-backend/scripts/staging/e2e_lead_capture.py` (staging browser test)
- `germaine-backend/tests/test_applicant_leads_capture.py`, `test_applicant_leads_admin.py`, `test_applicant_leads_postgres.py`

**Modified (small hooks; the same edits must be applied to the live versions)**
- `germaine-backend/app/blueprints/admissions/routes.py` — new `/leads/capture` route; post-commit linking hook in `create_application`
- `germaine-backend/app/blueprints/admin/__init__.py` — `import lead_routes`
- `germaine-backend/app/models/__init__.py` — register 2 models
- `germaine-backend/app/templates/admin/base.html` — "Applicant Leads" nav link
- `germaine-backend/app/static/admin/admin.css` — appended "APPLICANT LEADS" block (+ success/info flash styles)
- `build10/apply.html` — privacy notice + `<script src="assets/js/lead-capture.js">`
- `build10/assets/js/apply-wizard.js` — 3 hooks (programme event, send `lead_token`, clear token on success)
- `germaine-backend/tests/test_models_import.py` — registry 28 → 30

## 3. Database

**`applicant_leads`**: `id`, `lead_token_hash` (SHA-256, **UNIQUE** `uq_applicant_leads_lead_token_hash`), `applicant_name`, `phone_number` (as typed), `normalized_phone` (`2547…`/`2541…`), `email`, `programme`, `school`, `application_type`, `source_page`, `lead_status` (**CHECK**: new_lead / contacted / interested / follow_up_required / application_submitted / not_interested), `application_id` (**FK → applications.id ON DELETE SET NULL**), `first_captured_at`, `last_updated_at`, `last_activity_at`, `contacted_at`, `follow_up_notes`, `anonymized_at`, `created_at`, `updated_at`.
Indexes: `normalized_phone`, `lead_status`, `first_captured_at`, `application_id`.

**`applicant_lead_audit_logs`**: `id`, `lead_id` (no FK, so entries survive deletion), `admin_user_id` (FK SET NULL), `action`, `detail` (masked phone only — no name, email or full number), `created_at`.

No existing table, column, index or row is touched. **No cascades** in either direction.

## 4. Migration `c4d9e2a7b1f0`

- Hand-written. `flask db migrate` also proposed **dropping 9 existing indexes** (`ix_applications_referred_by_earncash_user_id` and 8 `ix_earncash_*`) because of existing model/migration drift. Those drops were deliberately excluded.
- Verified on PostgreSQL 16: upgrade → downgrade → upgrade is clean; downgrade removes only the 2 new tables; no model drift on the new tables.
- `down_revision` is currently `8b1f4c9d2e3a` (GitHub head) and **must be changed to the live head** (§12).

## 5. Endpoints

| Method | Path | Auth | Purpose |
|---|---|---|---|
| POST | `/api/admissions/leads/capture` | public | Create/update this browser's lead. Response is always `{"captured": true}` — never lead data |
| POST | `/api/admissions/applications` | public (existing) | Unchanged contract; links the lead **after** the existing commit |
| GET | `/admin/leads` | admin session | Stats, search, filters, sort, table |
| GET | `/admin/leads/<id>` | admin | Detail, possible duplicates, activity log, follow-up form |
| POST | `/admin/leads/<id>/follow-up` | admin + CSRF | Status / contact date / notes |
| GET | `/admin/leads/<id>/delete` | admin | Confirmation page |
| POST | `/admin/leads/<id>/delete` | admin + CSRF + `confirm=yes` (+ `confirm_linked=yes` if linked) | Delete lead row only |
| POST | `/admin/leads/<id>/anonymise` | admin + CSRF | Remove personal data, keep row |

## 6. Frontend (apply.html)

- Fields used: `#apFullname`, `#apPhone` (shown with a `+254` prefix), `#apEmail`, `#apSchool`, `#apProgramme` (hidden).
- `lead-capture.js` waits 1.2 s after the last keystroke and sends only when name and phone are both valid **and** something changed. In the E2E test, about 26 keystrokes produced 1 request. It retries quietly (3×, backoff) and makes a keepalive send on `pagehide`. It never shows pop-ups or errors.
- Privacy notice under the phone field. Capture is skipped if the notice isn't on the page.
- After a successful submit, the token is cleared, so a later new application from the same browser starts a new lead.

## 7. Admin dashboard

"Applicant Leads" sits under *Admissions* in the existing sidebar, using the same admin login, styles and pagination.
- Stats: Total, New Today (Nairobi day), Contacted, Interested, Incomplete, Completed, **Not Yet Contacted** (clickable).
- Table: Name · Phone · Email · Programme · Date Captured · Last Activity · Application Status · Follow-up Status · Actions (Call `tel:` · WhatsApp `wa.me` · Delete). It fits a 1280 px laptop screen and scrolls horizontally on phones.
- Search by name or by phone in any format (`0722 999`, `+254…`, last digits); filter by follow-up status, application status, not contacted; sort newest/oldest.
- Detail page: captured info, linked application, **possible duplicates** (same phone, other browser), activity log, follow-up form. "Application Submitted" can't be set by hand on an incomplete lead.
- Delete: a confirmation page names the applicant. A lead linked to an application shows a warning and needs an extra checkbox. The button disables after one click and the server is idempotent. *Anonymise instead* is offered for retention or erasure requests.

## 8. Security & privacy

- Server-side validation of every field; phone validated on both client and server; invalid data is never saved (422).
- Dedup by browser-token hash with `INSERT … ON CONFLICT DO NOTHING` plus `SELECT … FOR UPDATE`. 12 simultaneous requests for one token produced exactly 1 row on PostgreSQL. Never merged by name or phone; leads linked to an application are never overwritten by later captures.
- Throttling: 30 requests/min per IP, 15/min per token (per worker process). 4 KB body cap, honeypot field. IP is used only as an in-memory key and never stored.
- No lead data in any public response; errors return a generic 503 with no internals.
- Admin: existing `admin_required` + existing CSRF on every POST; no `/api/` exposure; CORS never applies to `/admin`.
- Audit log for follow-up changes, deletion and anonymisation, with masked phone only.
- Kenya Data Protection Act 2019: a visible notice before capture, only the necessary fields collected, plus anonymisation and deletion tools. *Review the notice wording against GTI's privacy policy before go-live.*

## 9. Tests (all run here against local throwaway databases; zero production data)

| Suite | Result |
|---|---|
| Full pytest (existing 214 + new 81) | **295 passed** |
| `test_applicant_leads_postgres.py` on PostgreSQL 16 | **5 passed** (migration head, 12-way concurrency → 1 row, CHECK, FK behaviour, clean downgrade) |
| Headless Chrome E2E on `apply.html` + staging API + Postgres | **14/14** |

Spec scenarios: **1** abandoned form → lead ✔ · **2** continue → same lead updated ✔ · **3** phone change ✔ · **4** revisit (same browser) ✔ · **5** submit → linked, first-capture time preserved ✔ · **6** invalid phone/name not saved ✔ · **7** keystrokes/retries → no duplicates ✔ · **8** same phone from another browser → kept separate and flagged ✔ · **9** API down or 503 → form submits, nothing shown ✔ · **10** delete incomplete lead, nothing else affected ✔ · **11** linked lead → warning, application intact ✔ · **12** unauthenticated/deactivated → denied ✔ · **13** status, notes and contact date persist ✔.

Also verified: CSRF rejection, HTML escaping, the 4 KB cap, the honeypot, throttling, idempotent delete, and that existing admin pages still render. Python 3.13 was used here. The code uses no features newer than 3.10, so it runs on the server's 3.12.

## 10. Staging environment used

Local only: PostgreSQL 16 on a private socket (`gti_staging`, `gti_test`), Flask dev server, `build10` on a static server, catalogue seeded with the repo's own `scripts/seed_catalogue.py`, and a staging-only admin. Nothing was written to the cPanel server or the production database.

## 11. Outstanding issues

1. **Production ↔ GitHub drift (most important).** Live code (63 files, 6 migrations) isn't in GitHub. Pulling it through the browser wasn't feasible: tool output is capped at about 2 KB per read, cPanel began throttling after about 20 reads, and then Chrome disconnected. **Recommended next step:** create a `production-snapshot` branch from the live source (excluding `.env*`, logs, `instance/`, `var/`, `tmp/`, venv, `*.bak*`), then rebase this feature branch onto it.
2. `down_revision` must be set to the live head (§12 step 2).
3. Hook edits must be re-applied to the **live** versions of the shared files (§12 step 4), not copied from this branch.
4. Rate limiting is per Passenger worker process (good enough against spam; dedup does not depend on it).
5. Existing in the repo: `apply.html` marks email as optional, but the GitHub `create_application` requires it. The live server appears to have fixed this (`applicant.py.pre-optemail`, migration `e5f2a9c1d7b3`). Leads are captured either way.
6. Existing: `apply-wizard.js` sends `"254" + phone`, so typing `07…` sends `2540…`. Lead normalization handles this; the application record does not.
7. Existing: `tests/test_cms.py` leaves 75-byte PNGs in `app/static/media/` on every run (cleaned here, not committed).
8. Existing: 9 indexes exist in migrations but not on the models (autogenerate drift — see §4).

## 12. Deployment instructions (for after approval — nothing below has been run)

> Do these in cPanel **Terminal** (or SSH), not by overwriting files from GitHub. Never paste `.env` contents anywhere.

**0. Backups**
```bash
TS=$(date +%Y%m%d-%H%M)
mkdir -p ~/_gti_backups/leads-$TS
cd /home2/germaine
tar --exclude='germaine-backend/.env*' --exclude='*/__pycache__' --exclude='*.log' \
    -czf ~/_gti_backups/leads-$TS/backend-src.tgz germaine-backend
cp germaineinstitute.ac.ke/apply.html germaineinstitute.ac.ke/assets/js/apply-wizard.js ~/_gti_backups/leads-$TS/
# Database backup (pg_dump reads DATABASE_URL from the app's environment; nothing is printed):
source ~/virtualenv/germaine-backend/3.12/bin/activate && cd ~/germaine-backend
python -c "import os,subprocess,dotenv;dotenv.load_dotenv('.env');u=os.environ['DATABASE_URL'].replace('+psycopg','');subprocess.run(['pg_dump','-Fc','-f',os.path.expanduser('~/_gti_backups/leads-$TS/db.dump'),u],check=True)"
```

**1. Read-only check.** Upload `scripts/predeploy_check_leads.py`, then run `python scripts/predeploy_check_leads.py`. Note the **single** Alembic head it prints and confirm every anchor is `[ok]`.

**2. Add new backend files** (from this branch) into `/home2/germaine/germaine-backend/`:
`app/models/applicant_lead.py`, `app/services/lead_service.py`, `app/utils/phone.py`, `app/utils/rate_limit.py`, `app/blueprints/admin/lead_routes.py`, `app/templates/admin/leads_list.html`, `lead_detail.html`, `lead_delete_confirm.html`, `migrations/versions/c4d9e2a7b1f0_applicant_leads.py`.
In the migration, change `down_revision = '8b1f4c9d2e3a'` to the head from step 1.

**3. Confirm the migration chain:** `flask --app wsgi db heads` must show only `c4d9e2a7b1f0`.

**4. Apply hook edits to the LIVE files** (small, additive — compare with this branch's diff):
- `app/models/__init__.py`: `from app.models.applicant_lead import ApplicantLead, ApplicantLeadAuditLog` and add both names to `__all__`.
- `app/blueprints/admin/__init__.py`: append `from app.blueprints.admin import lead_routes  # noqa`.
- `app/templates/admin/base.html`: add the "Applicant Leads" `<a>` after "Scholarship Applications".
- `app/static/admin/admin.css`: append the `/* APPLICANT LEADS (additive) */` block.
- `app/blueprints/admissions/routes.py`: add the imports, limiters, `capture_lead` route, and the `try: lead_service.link_application(...) except: rollback + log` block **immediately after** the live `create_application(payload)` call and before any notification code. Leave live notification/SMS/WhatsApp logic unchanged.

**5. Migrate:** `flask --app wsgi db upgrade`, then `flask --app wsgi db current`, which should report `c4d9e2a7b1f0`.

**6. Restart** — *only with your authorization*: cPanel → Setup Python App → germaine-backend → **RESTART**.

**7. Backend smoke test (creates no data):**
- `/api/health` → ok.
- `curl -X POST https://api.germaineinstitute.ac.ke/api/admissions/leads/capture -H 'Content-Type: application/json' -d '{}'` → **422** (validation works, nothing saved).
- Admin → Applicant Leads loads, showing 0 leads.

**8. Frontend** (`/home2/germaine/germaineinstitute.ac.ke/`): upload `assets/js/lead-capture.js`. Then apply the notice + `<script>` edits to the live `apply.html` and the 3 hooks to the live `apply-wizard.js`. `CORS_ALLOWED_ORIGINS` must already include `https://germaineinstitute.ac.ke` (it does for the existing forms — verify only, don't change). Confirm in your own browser's DevTools that typing a name and phone sends one `leads/capture` request returning 200. Then delete that lead from the dashboard; it was your own test.

**Rollback:** restore the backed-up files; `flask --app wsgi db downgrade <previous head>` (drops only the 2 new tables and the lead data); restart.
