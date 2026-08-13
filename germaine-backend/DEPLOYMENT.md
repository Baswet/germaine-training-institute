# Germaine Training Institute — Production Deployment Guide

This is a documentation + configuration package, not a record of an
actual deployment. I do not have access to your cPanel account, your
DNS provider, or your production PostgreSQL server from this
environment, and I never accept or enter hosting credentials on your
behalf — see "Why I can't do this part for you" at the end of this
file. Everything below is written so you (or whoever holds the cPanel
login) can carry it out directly.

The project has two independently-deployable pieces:

- **`germaine-backend/`** — the Flask API + server-rendered admin
  dashboard (PostgreSQL-backed).
- **`build10/`** — the public static site (HTML/CSS/JS), including
  EarnCash's static frontend. This is plain static files; no Python
  runtime needed to serve it.

The simplest, lowest-risk setup — and the one every relative URL in
this project already assumes — is deploying both under the **same
domain**, with the static site at the domain root and the backend
mounted so its `/api/...`, `/admin/...`, and `/health` routes are
reachable from that same origin. That avoids needing any CORS
configuration at all (`CORS_ALLOWED_ORIGINS` can stay empty).

---

## 1. Static site (`build10/`)

1. Upload the entire contents of `build10/` to your domain's public
   web root (cPanel: `public_html/`, or a subdirectory if this site
   doesn't own the whole domain).
2. Confirm `.htaccess`, `404.html`, `500.html`, `robots.txt`, and
   `sitemap.xml` (all at the root of `build10/`) uploaded correctly —
   these are what give the site branded error pages and correct
   search-engine behavior in production. Without `.htaccess`, 404s
   fall back to the hosting provider's default page instead of the
   site's own.
3. No build step, no `npm install` — these are plain static files.

## 2. Backend (`germaine-backend/`)

### cPanel "Setup Python App"

1. cPanel → **Setup Python App** → **Create Application**.
   - Python version: closest available to what this project was
     built/tested against (3.10+).
   - Application root: wherever you upload `germaine-backend/` on the
     server (does not need to be inside `public_html/` — cPanel
     Python apps are proxied, not served as static files).
   - Application URL: the subdomain or path this API should answer
     on. If you want it at the same domain as the static site with no
     separate subdomain, check your host's docs for reverse-proxying
     a Python app under a path prefix — otherwise the simplest option
     is a dedicated subdomain (e.g. `api.germaineinstitute.ac.ke`) and pointing
     the static site's `assets/js/api-client.js` override at it (see
     step 4 below).
   - Application startup file: `passenger_wsgi.py` (already in this
     project — cPanel/Passenger requires this exact filename at the
     application root).
   - Application Entry point: `application`.
2. Use cPanel's "Run Pip Install" (or the venv activate command it
   shows you) against `requirements.txt`.
3. Set environment variables. Copy `.env.production.example` to `.env`
   in the application root and fill in real values, **or** enter them
   individually in cPanel's "Environment Variables" section for this
   app — either mechanism works. At minimum you must set:
   - `FLASK_ENV=production`
   - `SECRET_KEY` — generate with
     `python -c "import secrets; print(secrets.token_hex(32))"`
   - `DATABASE_URL` — your real PostgreSQL connection string
   - `CORS_ALLOWED_ORIGINS` — only if the frontend ends up on a
     different origin than this API (see step 4)

### Database migration

Run this once, from the application's venv, against the real
production database, **before** the app receives any real traffic:

```
flask db upgrade
```

This applies all four migrations in order (`97e7ddbfa2e7` → initial
15-table schema, `2ac3535209b9` → CMS tables, `573ce201d310` →
EarnCash's 8 tables, `8b1f4c9d2e3a` → the EarnCash↔GTI referral bridge
columns). All four are additive — none of them drop or rewrite
existing data. Run `flask db current` afterward to confirm it reports
`8b1f4c9d2e3a (head)`.

If your database is not empty (e.g. you already ran migrations
manually or partially), run `flask db current` **first** to see what
it thinks is already applied before running `upgrade`, so you don't
apply anything twice against a database that's ahead of what
`alembic_version` recorded.

### Creating the first admin account

From the same venv, once the migration above has succeeded:

```
flask create-admin
```

This prompts interactively for name, email, and password (password
input is hidden, never accepted as a plain command-line argument, and
is hashed before being written to the database). Do this over SSH or
cPanel's Terminal — never through a web form, and never share the
resulting credentials over chat or email.

### Restart

Restart the app from cPanel's "Setup Python App" screen after setting
environment variables or applying migrations, so the running process
picks up the change.

## 3. Pointing the static site at the backend (if on different origins)

`build10/assets/js/api-client.js` auto-derives its API base URL from
the page's own origin for anything that isn't `localhost`/`127.0.0.1`
(fixed in Phase 15 — it previously always fell back to a hardcoded
`http://localhost:5000`, which would have silently broken every form
and catalogue/news read on the live site), so if the backend is
deployed at the **same origin** as the static site — `site.germaineinstitute.ac.ke`,
the recommended setup — no change is needed there.

If the backend ends up on a separate subdomain (e.g.
`api.germaineinstitute.ac.ke` while the site is at `site.germaineinstitute.ac.ke`), add this
one line before `api-client.js` loads, on every page (or via a single
shared include if your hosting setup supports server-side includes):

```html
<script>window.GERMAINE_API_BASE_URL = "https://api.germaineinstitute.ac.ke";</script>
<script defer src="assets/js/api-client.js"></script>
```

And set `CORS_ALLOWED_ORIGINS=https://site.germaineinstitute.ac.ke` in the backend's
environment so the browser is actually allowed to call it
cross-origin. EarnCash's own `EarnCash/frontend/js/config.js` derives
its API base the same way and needs no separate change.

## 4. DNS

- Point your domain's `A`/`CNAME` record at cPanel's IP/hostname per
  your host's instructions (this step happens in your domain
  registrar or DNS provider's dashboard, not in cPanel itself, unless
  your registrar and host are the same company).
- If using a separate API subdomain, add a matching `A`/`CNAME` record
  for it too.
- DNS propagation can take anywhere from minutes to ~48 hours
  depending on your provider and previous TTL settings.

## 5. SSL / HTTPS

- `SESSION_COOKIE_SECURE = True` is already hardcoded for production
  in `app/config.py` — the admin login session cookie will only be
  sent over HTTPS. **The admin dashboard will not work correctly over
  plain HTTP in production** — this is intentional (it's what makes
  the session cookie unstealable over an unencrypted connection), not
  a bug.
- Most cPanel hosts offer free AutoSSL (Let's Encrypt) — enable it for
  both the main domain and any API subdomain from cPanel's "SSL/TLS
  Status" page. This is normally a one-click action once DNS has
  propagated.
- Once SSL is active, confirm both `https://site.germaineinstitute.ac.ke` and (if
  used) `https://api.germaineinstitute.ac.ke` load without a certificate
  warning before considering the site launched.

## 6. Post-deploy verification checklist

Run through this once everything above is live:

- [ ] `https://site.germaineinstitute.ac.ke/` loads the public homepage
- [ ] `https://site.germaineinstitute.ac.ke/health` (or wherever the backend is
      mounted) returns `{"status":"ok","database":"connected",...}`
- [ ] A broken URL (e.g. `/this-does-not-exist`) shows the branded
      404 page, not the host's default error page
- [ ] `flask create-admin` account can log in at `/admin/login` over
      HTTPS
- [ ] Submitting the contact form, a newsletter box, and the
      apply/scholarship form on the live site actually reaches the
      admin dashboard's corresponding list views
- [ ] EarnCash registration → login → dashboard works against the
      live backend

---

## Why I can't do this part for you

You asked earlier in this conversation for the deployment itself to
be carried out, including cPanel/DNS/SSL steps, and offered to share
cPanel credentials. I want to restate clearly why I didn't take that
path, since it affects what "done" means for this phase: entering any
password — cPanel, DNS registrar, database, or otherwise — into any
field is something I'm never permitted to do, regardless of how it's
provided or authorized, and I don't have a secure credential-handling
mechanism in this environment for hosting logins. I also have no
direct network path from this sandbox to your live hosting account.
What I *can* do, and have done here, is everything that doesn't
require your credentials: the WSGI entry point, the production
environment template, the migration and admin-creation commands, and
this step-by-step guide — so the remaining steps are short, concrete,
and don't require deep familiarity with Flask or cPanel to execute.
