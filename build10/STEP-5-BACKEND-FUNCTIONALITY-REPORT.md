# Germaine Training Institute — Step 5 Backend Functionality Report

**Date:** August 11, 2026.

## Implemented

A real service layer (schools, departments, programmes with search/filter, applications with validated create + status lookup, scholarship info, alumni/graduate-request/partner-enquiry/contact-message/newsletter-subscription), wired into thin route handlers across the `public`, `admissions`, `alumni`, and `enquiries` blueprints, behind a consistent `{success, data, message}` / `{success, data:null, message, errors}` JSON envelope, backend-side validation on every write endpoint, centralized error handling (400/401/403/404/409/422/500, plus dedicated handlers for the new `ValidationError`/`NotFoundError` service exceptions), and transaction/rollback discipline on every write path. 79 tests pass (up from 18 at the end of Step 3/4), covering services, API routes, and database-level relationship/constraint/rollback behavior.

## Files Created

- `app/utils/responses.py` — `success()`/`error()` envelope helpers
- `app/utils/validation.py` — `Validator`, `ValidationError`, `NotFoundError`
- `app/services/scholarship_service.py`
- `app/services/engagement_service.py` (alumni, graduate requests, partner enquiries, contact messages, newsletter)
- `scripts/extract_frontend_data.js`, `scripts/seed_catalogue.py` (Step 4, listed here for completeness)
- `API_DOCS.md`
- `tests/_helpers.py`, `tests/test_services_catalogue.py`, `tests/test_services_application.py`, `tests/test_services_engagement.py`, `tests/test_api_catalogue.py`, `tests/test_api_admissions.py`, `tests/test_api_engagement.py`, `tests/test_db_interactions.py`

## Files Modified

- `app/services/programme_service.py`, `app/services/application_service.py` — replaced Step 3 `NotImplementedError` placeholders with real logic.
- `app/utils/errors.py` — extended with `401`/`403`/`422` handlers and hooks for `ValidationError`/`NotFoundError`; **all** error responses (including the pre-existing generic `400/404/409/500` ones) were migrated to the same `{success, data, message}` envelope Step 5 requires everywhere, rather than leaving two different error shapes in the same API. This is a deliberate consistency fix, not scope creep.
- `app/blueprints/{public,admissions,alumni,enquiries}/routes.py` — real routes replacing Step 3's placeholder/health-only content.
- `app/models/*.py` (all 15) — one-line, dialect-scoped compatibility change: `id = db.Column(db.BigInteger, primary_key=True)` → `db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)`. This was necessary because plain `BigInteger` primary keys don't auto-increment under SQLite (needed for the new relationship/transaction/constraint tests, which run against in-memory SQLite per the project's established "no live database required for tests" pattern). **It does not change the PostgreSQL column type at all** — re-ran `flask db migrate` against the real Step 4 database afterward and confirmed `No changes in schema detected`; the applied migration and all 353 seeded programme rows are untouched.
- `tests/conftest.py` — added `db_app`/`db_client` fixtures that call `db.create_all()`/`drop_all()` against a fresh in-memory SQLite database, scoped to a single test function. This is the first use of `create_all()` in this codebase; it is test-only, never runs against the real Postgres instance, and is the standard way to test ORM relationship/transaction/constraint behavior without a live server.
- `tests/test_app_factory.py` — one test updated to match the now-unified error envelope (see `errors.py` above).

## API Endpoints

See `germaine-backend/API_DOCS.md` for full detail (parameters, validation rules, status codes). Summary: `GET /api/health`, `GET /api/schools`, `GET /api/schools/<slug>`, `GET /api/schools/<slug>/departments`, `GET /api/programme-categories`, `GET /api/programmes`, `GET /api/programmes/<slug>`, `POST /api/admissions/applications`, `GET /api/admissions/applications/<reference_code>`, `GET /api/admissions/scholarship-info`, `POST /api/alumni/register`, `POST /api/enquiries/graduate-requests`, `POST /api/enquiries/partner-enquiries`, `POST /api/enquiries/contact-messages`, `POST /api/enquiries/newsletter-subscriptions`. The `admin` blueprint remains an intentional placeholder — no authentication system was built.

## Tests

`pytest`: **79 passed**, 0 failed, 0 warnings (18 pre-existing Step 3/4 tests + 61 new Step 5 tests: 30 service-layer, 22 API-layer, 5 database-interaction). `python -m compileall germaine-backend`: clean. All 79 run against in-memory SQLite — no live PostgreSQL server required. Separately, re-ran `flask db migrate` against the real Step 4 Postgres database to confirm the SQLite-compatibility model tweak produced zero schema drift there (`No changes in schema detected`), and re-verified all 15 tables and 353 seeded programme rows are untouched.

## Frontend Changes

**None.** No file under `build10/` was created, edited, or deleted in this step. No existing form was rewired to call any new endpoint.

## Database Changes

No schema change, no new migration, no new seed data. The only database-adjacent change was the SQLite-only `with_variant` compatibility tweak described above, verified to produce no diff against the real PostgreSQL schema from Step 4.

## Outstanding Items

Admin authentication/dashboard, RBAC, audit logging, `application_documents`/file uploads, a `graduates` directory, `employers`, payment processing, frontend integration (no existing page calls any of these endpoints yet), the external endpoint decision (§39 item E), and the other four/five still-open Step 2 §39 validation items (fee semantics, Business school naming, six short-course pages, `programme_inquiry` judgment call, and the alumni "Programme Studied" discrepancy found during the correction pass).

## Architecture Compliance

Confirmed against Steps 2-4: the unified `Programme` table with `programme_type` discriminator is used throughout (no duplicate AI programme structure); academic pricing is read from `School.fee`, AI Bootcamp pricing exclusively from `ProgrammeMode.fee_amount`/`fee_currency`/`start_date`, never mixed; `Application.reference_code` (never the sequential id) is the only application identifier ever returned publicly; no speculative entity (News, Vacancy, Employer, Graduates directory, ApplicationDocument, AuditLog, Role, Permission) was introduced; no payment processing, no admin authentication, and no frontend redesign occurred.
