# Germaine Training Institute — Final Production Report

Covers the triage-first execution of the 14-phase quality/security/deployment
directive, plus the earlier GTI Admin Dashboard one-click startup work and
the `referred_by_earncash_user_id` diagnosis. All work was done and verified
inside this sandbox against a disposable local database and the Flask test
client — nothing here was run against your real production PostgreSQL
database or your live hosting account (see Section L).

---

## A. What Was Fixed

**Critical — silently broken since Step 6 (site-wide form submission failure).**
`assets/js/main.js`'s generic `initForms()` attached a catch-all submit
handler to every `<form>` on the site. It ran before each page's real
backend-wired handler, reset the form fields and showed a fake "Thank you!"
message, which meant every real handler then saw empty required fields and
silently bailed via native validation — so contact, all 10 newsletter
instances, alumni registration, partner enquiry, graduate profile request,
the AI Bootcamp apply form, and the corporate-training consultation form
never actually reached the backend, despite showing a success message.
Reproduced live with a DOM event simulation (empty POST body before the
fix, correct payload after) and fixed via a claim pattern: each dedicated
handler now marks its form `data-form-handled`, and the generic handler
backs off entirely for those forms.

**Stored-XSS in the news article author field.** `news-article-detail.js`
built the author byline via `innerHTML` string concatenation instead of
`.textContent`, unlike every other field on that page — an admin-entered
author name could execute as JavaScript in every visitor's browser. Fixed
to build the icon as a real DOM element and set the author name via
`.textContent`.

**Raw exception details leaked to clients on 500 errors.** Three EarnCash
routes (`register`, `login`, `withdrawals/request`) returned
`{"error": ..., "details": str(e)}` on unhandled exceptions — potentially
exposing internal error text (DB detail, file paths) to any user who
triggered a server error. Fixed to log the real exception server-side only
and return a generic client-safe message.

**apply.html's newsletter box was never wired to the backend.** It used a
page-specific class (`ap-connect-form`) that the shared newsletter handler
didn't match, so it silently faked success (via the same generic-handler
bug above) with no dedicated handler at all, even after the collision fix.
Extended the newsletter handler's selector to include it — no HTML/CSS
changes, so the existing look is untouched.

**Missing branded error pages.** The public site had no custom 404/500
pages and no `.htaccess`, so a broken link or server hiccup would have
shown the hosting provider's bare default error page. Built both pages
matching the site's design system and an `.htaccess` with `ErrorDocument`
directives, `Options -Indexes`, and a dotfile-denial rule.

**`referred_by_earncash_user_id does not exist` (previously reported).**
Root cause: migration `8b1f4c9d2e3a` (adds the EarnFastCash↔GTI referral
bridge columns) exists correctly in the repo but was never actually run
(`flask db upgrade`) against the real production database. The migration
itself is correct, additive, and matches the models exactly — confirmed
via sandbox SQLite testing. See Section D for the exact command to run.

**Minor.** EarnCash's profile/password-change forms had no loading-state
button disable during the request, unlike every other form on the site —
added for consistency and basic duplicate-submission protection.

## B. What Was Already Correct (No Changes Needed)

- SQL injection: not possible anywhere — the whole backend uses SQLAlchemy
  ORM query methods exclusively; the one raw `execute()` call is a
  hardcoded `SELECT 1` health check with no user input.
- File uploads (CMS media library): already excellently hardened —
  magic-byte content sniffing (not just trusting the extension), a
  UUID-generated filename that eliminates path traversal entirely, a
  5MB size cap, and an image-type whitelist.
- No debug/dev endpoints, no hardcoded `debug=True`, no hardcoded secrets
  anywhere in the codebase.
- `DEBUG_ERRORS` and `DEBUG` are both `False` in `ProductionConfig`;
  session cookies are `HttpOnly` + `SameSite=Lax` always, `Secure` (HTTPS
  only) in every environment except local dev/testing.
- Admin dashboard: CSRF protection, session-based auth, inactive-admin
  rejection, logout requiring a CSRF-protected POST (not a bare GET),
  and zero `|safe` template bypasses anywhere — all confirmed via the
  existing 35-test admin suite plus a fresh live login → dashboard →
  logout → re-block verification this session.
- EarnCash referral attribution: valid/unknown/absent/suspended-referrer
  cases all behave correctly and are structurally immutable per
  application (Applications are always freshly inserted, never updated
  in place, so there's no overwrite path).
- All 14 AI Bootcamp programme cards match their underlying data exactly
  (routing, category, price) with zero drift, and all 16 AI Bootcamp
  family pages correctly hide the main site header via `aic-family-page`.
- The Enrollments gateway offers exactly two choices (AI Bootcamps,
  Academic Schools), both correctly routed and escaped.
- Every EarnCash admin/user dashboard screen (admin panel, dashboard,
  referrals, notifications, withdrawals) already escapes every
  user-controlled field before rendering — the one CMS-side gap (author
  field, above) was the only real exception found.
- Viewport meta tags present on all 72 pages; comprehensive breakpoint
  coverage (320–1440px) across every major stylesheet; tables already
  wrapped for horizontal scroll on small screens.

## C. What Remains (Not Attempted, Explicitly Out of Scope Here)

- Live browser rendering verification (visual regression at each
  breakpoint, console/network inspection) — no real browser is available
  in this sandbox; all responsive/UI work was a static code review only.
- Actual cPanel/DNS/SSL deployment execution — see Section L.
- Older, lower-priority backlog items not referenced in your most recent
  instructions (EarnCash admin-account live testing, referral/commission
  live display on the admin applications view, EarnCash courses/enrollment
  live flow) — flagged in earlier phases as blocked on a real admin
  account or real payment data, not attempted here since they weren't
  part of this directive.

## D. Database Changes

**No schema changes were made in this session.** The one outstanding
migration (`8b1f4c9d2e3a`) already existed in the repo before this
session started — it was diagnosed, not created, and is purely additive
(adds `applications.referred_by_earncash_user_id`,
`applications.tuition_confirmed_at`, and the new
`earncash_application_commissions` table; drops nothing, rewrites
nothing).

To bring your real production database in sync, run this once from the
backend's environment:

```
flask db upgrade
```

Then confirm with `flask db current` — it should report
`8b1f4c9d2e3a (head)`. Full detail in `DEPLOYMENT.md`.

## E. Tests + Results

- Backend: **204/204 pytest tests passing** (final run, after every
  change in this session).
- Frontend: all 59 JavaScript files across the whole site pass
  `node --check`; all 72 HTML files (57 top-level + 11 EarnCash + the 2
  new error pages) pass HTML tag-balance verification.
- Live-executed verification (via Flask's test client, not just static
  review): admin login → CSRF-protected dashboard access → CSRF-protected
  logout → access correctly denied afterward; a nonexistent `/admin/...`
  path returns a clean JSON 404 with no stack trace; `/health` and
  `/api/...` 404s behave the same way; all four EarnCash referral
  attribution scenarios (valid, unknown, absent, suspended) pass.
- The `initForms()` collision bug and its fix were verified with a real
  DOM/event-dispatch simulation (jsdom), not just code reading — captured
  the actual POST body sent to a stubbed backend before and after the fix.

## F. Production Package Created

Three new files, all in `germaine-backend/`:

- **`passenger_wsgi.py`** — the exact entry point cPanel's "Setup Python
  App" / Phusion Passenger requires (`application` callable).
- **`.env.production.example`** — production environment template
  (`FLASK_ENV=production`, `SECRET_KEY` generation instructions,
  `DATABASE_URL`, `CORS_ALLOWED_ORIGINS`). No real values filled in.
- **`DEPLOYMENT.md`** — the full step-by-step guide condensed into
  Sections G–I below.

Plus, in `build10/`: **`404.html`**, **`500.html`**, and **`.htaccess`**
(Phase 4, Section A).

## G. Exact cPanel Steps

1. Upload `build10/`'s contents to your public web root.
2. cPanel → **Setup Python App** → **Create Application**:
   - Python 3.10+
   - Application root: wherever you upload `germaine-backend/`
   - Application startup file: `passenger_wsgi.py`
   - Application Entry point: `application`
3. Run pip install against `requirements.txt` (cPanel provides a button
   or venv-activate command for this).
4. Set environment variables from `.env.production.example` (as a real
   `.env` file or via cPanel's Environment Variables screen).
5. From the app's venv: `flask db upgrade`, then `flask create-admin`
   (Section J).
6. Restart the app from the Setup Python App screen.

Full detail, including what to do if the backend ends up on a separate
subdomain from the static site, is in `DEPLOYMENT.md`.

## H. Exact DNS Records

This depends on your domain registrar and hosting provider, which I have
no access to from this sandbox, so I can't give you literal record
values — but structurally:

- An `A` or `CNAME` record at your registrar pointing your domain at
  cPanel's IP/hostname (your host's control panel shows you the exact
  target value to use).
- If deploying the backend on a separate subdomain (e.g.
  `api.yourdomain.com`), a second `A`/`CNAME` record for that subdomain.
- Expect propagation to take anywhere from minutes up to ~48 hours.

## I. Exact SSL Requirements

- `SESSION_COOKIE_SECURE = True` is hardcoded for production — **the
  admin dashboard will not accept the session cookie over plain HTTP**,
  by design.
- Enable your host's free AutoSSL (Let's Encrypt) for the main domain
  and any API subdomain from cPanel's "SSL/TLS Status" page — normally
  one click once DNS has propagated.
- Verify both the main domain and any API subdomain load over HTTPS with
  no certificate warning before considering the site launched.

## J. Exact Admin-Creation Command

From the backend's production venv, over SSH or cPanel's Terminal
(never through a web form, never shared in chat):

```
flask create-admin
```

Prompts interactively for name, email, and password. Password input is
hidden and hashed before being written to the database — never passed as
a plaintext argument, never logged.

## K. Final Admin URL

`https://<your-production-domain>/admin/login`

(Locally, during development, this is `http://127.0.0.1:5000/admin/login`,
reachable via the existing `start-admin.bat` one-click launcher.)

## L. Remaining Blockers

**I did not perform the actual deployment, and I want to be direct about
why**, since you explicitly asked earlier in this conversation for the
cPanel/DNS/SSL work to be carried out and offered to provide credentials.
Entering any password — cPanel, domain registrar, database, or otherwise
— into any field is something I'm never permitted to do, regardless of
how it's provided or authorized, and this environment has no secure
credential-handling mechanism for hosting logins. I also have no direct
network path from this sandbox to your live hosting account. I did not
ask you to resend those credentials, and please don't paste them into
chat.

What this means concretely: everything that doesn't require your
credentials is done and verified (the code fixes, the migration, the
WSGI entry point, the environment template, and the deployment
documentation). The remaining steps — uploading files, running the
migration/admin-creation commands on the real server, configuring DNS,
and enabling SSL — need to be carried out by you or whoever holds the
hosting account, following Sections F–J above. None of them require deep
Flask or cPanel knowledge; they're short and concrete by design.

No production data was touched, no database was recreated, and no
credentials were requested, stored, or acted upon anywhere in this
session.
