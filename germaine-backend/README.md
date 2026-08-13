# Germaine Backend

Flask backend scaffold for the Germaine Training Institute website, built from
the approved **Step 2 — Database Architecture** design
(`build10/STEP-2-DATABASE-ARCHITECTURE.md`). This is a **Step 3** deliverable:
project structure, SQLAlchemy models, and blueprint architecture only.

## What this is NOT

This scaffold does not create, connect to, or populate a live database. There
is no PostgreSQL server running against it, no table has been created, no
migration has been run, and no seed data exists anywhere in this repository.
It also does not touch, rewire, or redesign anything in the existing frontend
(`build10/`) — no existing form (`apply.html`, `alumni.html`,
`graduate-hire.html`, `partner-with-us.html`, `corporate-training.html`,
`contact.html`, the newsletter forms, `ai-bootcamp.html`) was modified or
pointed at this backend.

## Architecture

```
germaine-backend/
  app/
    __init__.py        Application factory (create_app)
    config.py           Environment-variable-driven config (dev/testing/production)
    extensions.py        Shared db (SQLAlchemy) / migrate (Flask-Migrate) instances
    models/               15 models, one file each, matching Step 2 §28 exactly
    blueprints/
      public/             The only blueprint with a real route: GET /api/health
      admissions/          Placeholder — future Applicant/Application API
      alumni/               Placeholder — future Alumni API
      enquiries/            Placeholder — future GraduateProfileRequest/PartnerEnquiry/
                            ContactMessage/NewsletterSubscriber API
      admin/                Placeholder — future authenticated dashboard API
    services/              Routes -> Services -> Models -> Database layering,
                            placeholder files only (programme_service.py,
                            application_service.py, auth_service.py)
    utils/
      security.py           Password hashing (Werkzeug PBKDF2-SHA256)
      reference_code.py     Application.reference_code generator (never the sequential id)
      errors.py             Centralized JSON error handlers (400/404/409/500)
  migrations/             Flask-Migrate/Alembic scaffold — initialized via
                          `flask db init` only. No migration has been generated
                          or run (migrations/versions/ is empty).
  tests/                  App creation, health endpoint, config loading, and
                          model-import tests. Uses an in-memory SQLite URI
                          purely so Flask-SQLAlchemy can initialize — no live
                          PostgreSQL server is required to run this suite, and
                          no test calls db.create_all() or queries a table.
  wsgi.py                 Local dev entry point
  requirements.txt        Flask, Flask-SQLAlchemy, Flask-Migrate, python-dotenv, psycopg — nothing else
  .env.example             Placeholder environment variables only
  .gitignore
```

## The 15 models (Step 2 §28)

Phase 1 (14): School, Department, ProgrammeCategory, Programme, ProgrammeMode,
ProgrammeFAQ, ProgrammeFeature, Applicant, Application, Alumni,
GraduateProfileRequest, PartnerEnquiry, ContactMessage, NewsletterSubscriber.

Phase 2 (1): AdminUser.

Academic and AI Bootcamp programmes share one `Programme` table
(`programme_type` discriminator), per Step 2 §7. Academic fees live on
`School.fee` (flat string); AI Bootcamp fees live on
`ProgrammeMode.fee_amount` (nullable decimal — `NULL` means "Contact
Admissions", never a stored literal string), per Step 2 §8. No speculative
models (News, Vacancy, Employer, Graduate directory, ApplicationDocument,
AuditLog, Role, Permission) are included — see Step 2 §35 for what was
deliberately deferred and why.

## Setup (local development)

```bash
cd germaine-backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in a real SECRET_KEY and DATABASE_URL locally
```

Running the app locally (`flask --app wsgi run` or `python wsgi.py`) will only
succeed once a real `DATABASE_URL` is set — this scaffold does not create that
database for you, on purpose.

## Running the tests

```bash
python3 -m pytest -q
```

No live PostgreSQL server is required. All 18 tests exercise app creation,
the `/api/health` endpoint, config resolution, and model registration/shape —
none of them touch a real database.

## Migrations

`migrations/` was created via `flask db init` only. No `flask db migrate`
(autogenerate) or `flask db upgrade` (apply) has been run — there is no
migration file in `migrations/versions/` and no schema has been applied
anywhere. Generating and running the first migration against a real
PostgreSQL database is future work, explicitly out of scope for this step.

## Database status

**No live database was created or populated as part of this step.** See
`build10/STEP-2-DATABASE-ARCHITECTURE.md` for the full schema design this
scaffold implements structurally, and its §39 for open questions (school fee
semantics, a school-naming inconsistency, six short-course pages' real data
source, and the `programme_inquiry` application-type judgment call) that
still need confirmation before any seed/migration step runs against real
data.

## Frontend status

**Nothing in `build10/` was changed as part of this step.** No existing form
was rewired, no fetch() call was replaced, and no HTML/CSS/JS was touched.
