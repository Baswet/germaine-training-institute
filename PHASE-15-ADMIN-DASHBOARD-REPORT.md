# Phase 15 — Admin Dashboard Completion, Reliability & Deployment Readiness

Continuation of the Germaine Training Institute production work. Scope: audit
and harden the GTI Admin Dashboard end-to-end, close the EarnCash admin
account gap, verify the production deployment package against the real
domain, and re-run the full regression suite. No database schema was
changed, no existing functionality was removed, and no production
credentials were requested, entered, or stored (see Section E and the
security note at the end).

**A note on the cPanel password sent in chat:** a real cPanel password was
included in the message that started this phase. It was not used, stored,
written to any file, or repeated back — but since it's now in this
conversation's history, it should be treated as exposed and rotated in
cPanel as routine hygiene. Everything below was produced without logging
into any hosting account, because this environment has no network path to
one and passwords are never handled here regardless of how they're offered.

---

## A. Completed

**Closed the EarnCash admin account gap (the real blocker behind old tasks
#274/#275).** There was no supported way to create an EarnCash admin
account at all — the public registration endpoint always creates
`role='user'` by design, so the only way to get an admin account was
direct, unaudited database editing. Added `flask create-earncash-admin`,
mirroring the existing `flask create-admin` pattern exactly: interactive
password prompt (never a CLI argument, never echoed), Werkzeug PBKDF2-SHA256
hashing, duplicate-email rejection, weak-password rejection, and an explicit
refusal to silently promote an existing regular user to admin (that has to
be a deliberate, separate action). Verified live: the created account logs
in successfully through the real `/api/earncash/admin/login` route and
receives a working JWT.

**Fixed a real production-blocking bug in `api-client.js`.** The GTI site's
central API client — used by every backend-connected form (contact,
newsletter, alumni, partner enquiry, graduate profile request, AI Bootcamp
apply, corporate training consultation) plus every catalogue/news/site-content
read — fell back to a hardcoded `http://localhost:5000` whenever
`window.GERMAINE_API_BASE_URL` wasn't explicitly set, which no page in the
site actually does. Deployed as-is, this meant every one of those requests
would have tried to reach the *visitor's own machine* instead of the real
backend: a silent, site-wide outage on day one of production. This directly
contradicted `DEPLOYMENT.md`'s existing claim that the client "already
auto-derives its API base URL from the page's own origin." It didn't; now
it does, mirroring the pattern EarnCash's own `config.js` already used
correctly. Verified with a live jsdom simulation: on `localhost`, requests
still target `localhost:5000` (unchanged dev behavior); on
`site.germaineinstitute.ac.ke`, requests now correctly target that same
origin, with zero configuration needed for the standard same-origin
deployment `DEPLOYMENT.md` recommends.

**Added automated test coverage for both CLI commands.** Neither
`create-admin` nor the new `create-earncash-admin` had any pytest coverage
before this phase — they'd only ever been exercised manually. Added
`tests/test_cli.py` (10 tests): hashed-password verification, duplicate-email
rejection, email lowercasing, the new command's role/status defaults, a live
login through the real route, and the "refuse to silently promote" guard.

**Updated `DEPLOYMENT.md` and `.env.production.example`** to reference the
real production domain (`site.germaineinstitute.ac.ke`, provided this
session) instead of the `yourdomain.com` placeholder, and corrected the
inaccurate api-client.js claim described above.

## B. Admin Dashboard — Section-by-Section Verification

Every item below was actually executed against a live Flask test client
this session (in-memory SQLite, real routes, real templates, real CSRF) —
not inferred from reading code.

```
PASS — Login (valid credentials -> dashboard redirect)
PASS — Login (invalid credentials -> generic error, stays on login page)
PASS — Login (missing/bad CSRF token -> 403)
PASS — Unauthenticated access to /admin/ -> redirect to /admin/login?next=...
PASS — /admin, /admin/, /admin/login route consistency (clean 308/200/302, no loops)
PASS — Dashboard (loads with real seeded data)
PASS — Applications (list, detail, status update with CSRF, invalid-status rejection, 404 for missing id)
PASS — Scholarships (filtered application list)
PASS — Alumni (list, detail — confirmed read-only by design, no status-update route)
PASS — Contact Enquiries (list, detail, status update)
PASS — Graduate Profile Requests (list, detail, status update)
PASS — Partnerships / Corporate Training (list, detail, status update, correctly separated by enquiry_type)
PASS — Newsletter Subscribers (list, read-only by design)
PASS — Website Content editor (loads all registry groups, save persists a real value)
PASS — Homepage/Student Life content lists (create, update, archive list items)
PASS — News (full lifecycle: create draft -> publish -> unpublish -> archive, all verified live)
PASS — Media Library (list with empty state; upload path already validated by existing tests — magic-byte sniffing, extension whitelist, UUID filenames)
PASS — Academics: Schools (list, edit, update persists)
PASS — Academics: Programmes (list, edit; existing tests confirm update never silently touches fee data)
PASS — Academics: Categories (list, edit)
PASS — Logout (CSRF-protected POST; session destroyed; protected route immediately rejects afterward)
PASS — EarnCash Admin (separate JWT-authenticated system by design — see note below; login, stats,
       users list, withdrawal approve/reject, enrollment payment verification, course creation all
       covered by existing tests; account-creation gap closed this phase, live login verified)
```

**On EarnCash's admin panel being separate from `/admin/`:** this is not an
oversight — `app/blueprints/earncash/admin_routes.py`'s own docstring states
it deliberately: EarnCash's admin surface (JWT, `earncash_users.role='admin'`)
and Germaine's staff portal (session cookie, `admin_users` table) are two
independent systems that can never authenticate against each other, each
with its own frontend (`build10/EarnCash/frontend/pages/admin*.html` vs.
`/admin/*` Jinja templates). Merging them into one sidebar would have meant
building a duplicate system, which the standing instructions explicitly
prohibit. Both are now genuinely usable; neither was touched architecturally.

**Local one-click startup (`start-admin.bat`/`.ps1`)** was audited, not
rewritten — it already correctly locates the project's `.venv`, verifies
dependencies and `.env`, runs a read-only DB connectivity + migration-state
preflight before starting anything, waits for `/health`, and opens the
browser straight to `/admin/login`. No repair was needed.

## C. Tests + Results

```
pytest:              214/214 passing   (204 baseline + 10 new tests/test_cli.py tests)
JavaScript syntax:   59/59 files clean (node --check, assets/js/ + EarnCash/frontend/js/)
HTML validation:     72/72 files clean (tag-balance check, build10/ + EarnCash/frontend/pages/)
Backend py_compile:  clean across every .py file under germaine-backend/app/
Admin auth lifecycle live-tested via Flask test client: login/invalid-login/
  unauthenticated-redirect/logout/post-logout-rejection/CSRF-both-directions/
  404-for-missing-records — all passing, evidence in Section B.
```

Every number above was produced by an actual command run this session, not
carried over from memory.

## D. Database

- Current local migration chain, unchanged this session: `97e7ddbfa2e7`
  (root) → `2ac3535209b9` (CMS) → `573ce201d310` (EarnCash) →
  `8b1f4c9d2e3a` (EarnFastCash↔GTI referral bridge, **head**). Confirmed
  directly from each migration file's `down_revision` chain.
- No new migration was created. No schema change of any kind was made this
  phase — every fix was code-level (CLI command, JS bug, docs).
- **This sandbox has no PostgreSQL server available this session** (fresh
  environment; no root access to install one), so `flask db upgrade` /
  `flask db current` could not literally be re-run here. All pytest and live
  route testing instead used the project's existing in-memory-SQLite test
  harness (`tests/conftest.py`'s `db_app` fixture, which every test in the
  204-baseline suite already relies on), which is honest, real coverage —
  just not a substitute for confirming migration state against the actual
  production database.
- Migration `8b1f4c9d2e3a` still needs to be applied to the real production
  database — this was already true before this phase and remains the one
  concrete database action left. Command: `flask db upgrade`, then verify
  with `flask db current` (expect `8b1f4c9d2e3a (head)`).

## E. Remaining Issues (genuine blockers only)

1. **Actual production deployment has not happened.** Nothing in this
   environment can reach cPanel, DNS, or a live PostgreSQL server — this
   was true before Phase 15 and remains true now. `DEPLOYMENT.md` has the
   exact steps.
2. **`flask db upgrade` has never been run against the real production
   database.** This is the one concrete database action outstanding.
3. **No real production admin account exists yet** (neither GTI's
   `admin_users` nor EarnCash's `earncash_users` role='admin') — both are
   one command away (`flask create-admin` / `flask create-earncash-admin`)
   but must be run on the real server, over SSH/cPanel Terminal, by whoever
   holds that access.
4. Everything else flagged as "remaining" in the earlier FINAL-PRODUCTION-REPORT.md
   (live-browser visual regression, DNS/SSL execution) is unchanged and
   still applies for the same reason — no browser or hosting access from
   this sandbox.

## F. Exact Steps To Finish (only the parts requiring your access)

These are unchanged in substance from `DEPLOYMENT.md`, restated here with
the real domain now that it's known:

```
1. Upload build10/ contents to the public web root for site.germaineinstitute.ac.ke
2. cPanel -> Setup Python App -> create/configure germaine-backend/
     Python 3.10+, startup file passenger_wsgi.py, entry point "application"
3. pip install -r requirements.txt (via cPanel's Run Pip Install)
4. Set environment variables from .env.production.example:
     FLASK_ENV=production
     SECRET_KEY=<generate fresh: python -c "import secrets; print(secrets.token_hex(32))">
     DATABASE_URL=<your real production PostgreSQL URL>
     CORS_ALLOWED_ORIGINS=   (leave empty for the standard same-origin setup)
5. flask db upgrade          (applies the one outstanding migration)
6. flask db current          (confirm it reports 8b1f4c9d2e3a (head))
7. flask create-admin        (GTI staff portal admin — interactive prompt)
8. flask create-earncash-admin   (EarnCash admin — interactive prompt, new this phase)
9. Restart the Python app from cPanel's Setup Python App screen
10. Point DNS (A/CNAME) at your host's IP/hostname for site.germaineinstitute.ac.ke
11. Enable AutoSSL/Let's Encrypt for the domain
12. Verify: https://site.germaineinstitute.ac.ke/ loads, /health returns ok,
    https://site.germaineinstitute.ac.ke/admin/login accepts the account from step 7,
    a broken URL shows the branded 404, and a real form submission (e.g. contact)
    actually reaches the admin dashboard's list view.
```

Steps 2, 4 (entering the real `SECRET_KEY`/`DATABASE_URL` values), 7, 8, 10,
and 11 all require direct access to cPanel/DNS/PostgreSQL that this
environment does not have — these remain yours to execute. Everything else
(the code, the migration file, the CLI tools, the docs) is ready now.
