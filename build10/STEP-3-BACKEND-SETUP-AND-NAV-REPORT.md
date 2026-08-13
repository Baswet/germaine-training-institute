# Germaine Training Institute — Step 2 Corrections, Global Navigation Consistency, and Step 3 Backend Scaffold: Final Report

**Date:** August 11, 2026.

---

## Part 1 — Step 2 Document Corrections

**Correction (this pass):** the sentence below previously read "was edited (not rewritten) in two places," which was itself imprecise. Corrected wording: `STEP-2-DATABASE-ARCHITECTURE.md` was modified only in **§1** (Executive Summary table-count wording), **§5**, **§9** (applicant-matching wording), **§11** (alumni discrepancy note), and **§39**; no other section was changed.

**§1 "Executive Summary"** previously stated "The result is **14 tables for Phase 1+2 (MVP + Admin)**" — this incorrectly read as if 14 were the grand total. Corrected to: "The result is **15 tables across Phase 1 and Phase 2: 14 Phase 1 tables plus 1 Phase 2 admin table**."

**§5 "Final Entity List"** reads as two separate, explicitly labeled groups instead of one flat 1-15 list: "**Phase 1 — 14 tables**" (numbered 1-14), followed by "**Phase 2 — 1 additional table**" (15. `admin_users`), followed by "**Final total: 15 tables total = 14 Phase 1 + 1 Phase 2**." This same framing is cross-referenced consistently everywhere else the count appears in the document (§33-34, §38) — nothing implies all 15 tables belong to Phase 1.

**§39 "Risks / Open Questions"** is titled "**VALIDATION REQUIRED BEFORE SEEDING**" and contains **five** lettered items, each explicitly preserved as open rather than silently resolved (a prior version of this report incorrectly described this section as containing only four items, A-D, omitting E — that was a reporting error, corrected here):

- **A. School fee semantics** — `schools.fee` stays a display string, not converted to a numeric per-programme fee, until you confirm whether it's a fixed price or a "starting from" figure.
- **B. Business school naming** — the "School of Business & Commerce" vs. "Business & Social Sciences" inconsistency is flagged for your confirmation of the canonical name, not arbitrarily chosen.
- **C. Six short-course pages** — their real data source was not found inside `school-data.js` during Step 0.5 and is not assumed; needs verification before migration.
- **D. `application_type = 'programme_inquiry'`** — the unification of the AI Bootcamp inquiry form under the main `applications` table remains flagged as an architectural judgment call for your review, not a verified frontend requirement. No frontend or database change was made because of it.
- **E. The existing external application endpoint** (`germaineinstitute.com/application/clients/add`) — the architecture deliberately does not depend on it, but before any frontend integration someone must decide whether it is replaced, integrated, bridged temporarily, or retired. This item was always present in §39 itself; it was the prior version of *this report's summary* of §39 that dropped it, not the underlying Step 2 document.

**A sixth item, F, was newly identified during this correction pass** while re-verifying the alumni relationship (§11) directly against `alumni.html`: the field labelled "Programme Studied" (`#aluProgramme`) actually offers only school names plus an AI Bootcamp catch-all as its options — it is a school-level selector wearing a programme-level label. `alumni.programme_id → programmes.id` was left unchanged; this is now flagged in §39 as item F, pending your decision on how to reconcile the FK with what the form actually collects.

**§9 "Admissions / Application Model"** previously described `applicants` as "looked up/created by email+phone," which could be read as implying a composite matching key that the table specification never defined (`applicants.email` alone is `UNIQUE`). Corrected to state that applicants are matched primarily by their unique email address, with phone retained as an additional identifying/contact field, not a second matching key. No model change was made.

---

## Part 2 — Global Navigation Consistency Audit + Corrections

**Method:** rather than assume where inconsistencies might be, every page's body class was checked against every CSS file for nav-scoped selector overrides (`.navbar`, `.nav-links`, `.dropdown-menu`, `.fixed-top-stack`, `.utility-bar`, `.branding-bar`, `.hamburger`, `.apply-btn`, `.mega-menu`, etc.), and both `main.js` and `header-premium.js` were read in full to confirm there is exactly one authoritative scroll/hysteresis handler and one dropdown/accessibility handler.

**Pages/files inspected:** `assets/js/main.js`, `assets/js/header-premium.js`, `assets/css/style.css`, `assets/css/nav-refresh.css`, `assets/css/responsive.css`, `assets/css/global-refinements.css`, and every page-specific CSS file with a `body.*-page` class (`graduate-hire-elevate.css`, `contact-page.css`, `scholarship.css`, `student-life.css`, and the remainder, which had no nav-selector overrides at all), across all 58 real HTML pages (Home, About, Schools hub + individual school pages, programme pages, AI Bootcamp hub + all 14 detail pages, admissions/apply, alumni, graduate-hire, partner-with-us, corporate-training, contact, student-life, and the rest) plus the intentionally-orphaned `hero-template.html`.

### Findings and fixes

**1. Dead-effect duplicate scroll handler (`assets/js/main.js`).** `initNavbarTransparency()` toggled a `.solid` class on `#header` using a non-hysteresis `scrollY < 30` threshold — a second, cruder scroll mechanism running alongside the correct `initStickyHeader()` hysteresis handler (`ACTIVATE_AT=80` / `DEACTIVATE_AT=60`). `.solid` has zero matching CSS anywhere in the project, so it had no visible effect today, but it was still a genuine duplicated implementation with different logic. **Fix:** removed the call site from the init sequence; one scroll-state mechanism (`initStickyHeader()`) now drives the header everywhere. The dead function body was also removed and replaced with an explanatory comment.

**2. Page-unique navigation re-theme (`assets/css/graduate-hire-elevate.css`).** This was the one real, substantial inconsistency: a ~190-line `body.ghire-page`-scoped block gave the Hire Our Graduates page its own navy/purple travelling-light nav theme — custom CSS variables, gradient-text active links, a glowing floating logo, and a uniquely styled Apply button — found nowhere else in the project (verified by the same grep sweep against all other page-classed CSS files). **Fix:** removed the entire block, replaced with an explanatory comment. The page now inherits the same shared navigation component (colors, hover, active state, dropdowns, Apply button, scroll behavior) as every other page, via `style.css` / `nav-refresh.css` only. A stray leftover selector reference inside an unrelated reduced-motion rule further down the same file was also corrected. Nothing else in this file — hero, testimonials, FAQ, footer touches, ripple effects — was changed.

**3. Three harmless redundant re-assertions (`contact-page.css`, `scholarship.css`, `student-life.css`).** Each has one line re-declaring `.fixed-top-stack{ position:fixed !important; top:0 !important; left:0 !important; width:100% !important; z-index:1000 !important; }`, explicitly commented "Guarantee true fixed positioning... matching the homepage's sticky-nav behaviour exactly." These values are byte-identical to the base rule already in `style.css` — no color, animation, or layout divergence — so they were left as-is; removing them would be a no-op change with no user-visible effect, and it's not the kind of "duplicated implementation" the audit was meant to catch (nothing here actually differs from the shared nav).

### Verified consistent (no changes needed)

- **Mobile navigation:** identical hamburger markup (`id="hamburgerBtn"`, `aria-controls="sideNav"`) and identical `main.js` + `header-premium.js` script pair on all 57 real pages.
- **Header-height / content offset:** `.page-shell`'s fixed-header offset in `style.css` is shared sitewide; `graduate-hire-elevate.css` never overrode padding/margin/offset values (confirmed via grep before and after the fix), so removing its nav block introduced no gap or jump.
- **Dropdowns/active-state:** no page beyond the now-fixed `graduate-hire.html` had any dropdown or active-link color/behavior override.
- **Syntax integrity:** `node --check` on `main.js` and `header-premium.js`, and brace-balance verification on `graduate-hire-elevate.css` (124 open / 124 close), both clean after edits.

**Explicitly not touched, per scope:** hero sections, programme/school/AI Bootcamp cards, footer designs, page backgrounds, section layouts, images/cropping, unrelated animations/typography, CTAs, forms, content/copy, programme/school structures, clubs/societies, student-life/alumni/partner page sections.

---

## Part 3 — Step 3: Backend Project Architecture & Flask Setup

### Files created

A new, separate project — **`germaine-backend/`** — was created as a sibling of `build10/` (not inside it, consistent with `build10` being treated as a pure static-frontend directory throughout this engagement):

```
germaine-backend/
  app/
    __init__.py, config.py, extensions.py
    models/            15 files, one per table, + __init__.py registry
    blueprints/         public (real /api/health route), admissions,
                        alumni, enquiries, admin (all 4 others: placeholder only)
    services/           programme_service.py, application_service.py,
                        auth_service.py — placeholders
    utils/               security.py, reference_code.py, errors.py
  migrations/            Flask-Migrate scaffold (flask db init only)
  tests/                 6 files, 18 tests total
  wsgi.py, requirements.txt, .env.example, .gitignore, README.md
```

52 files total. Full contents mirrored in the workspace at `germaine-backend/`.

### Models — all 15 confirmed present and matching Step 2 §28 exactly

Phase 1 (14): `School`, `Department`, `ProgrammeCategory`, `Programme`, `ProgrammeMode`, `ProgrammeFAQ`, `ProgrammeFeature`, `Applicant`, `Application`, `Alumni`, `GraduateProfileRequest`, `PartnerEnquiry`, `ContactMessage`, `NewsletterSubscriber`.
Phase 2 (1): `AdminUser`.

No speculative models exist (`News`, `Vacancy`, `Employer`, a `Graduates` directory, `ApplicationDocument`, `AuditLog`, `Role`, `Permission`) — a dedicated test (`test_no_forbidden_speculative_models_defined`) asserts this.

Key design constraints from Step 2 were carried through exactly:
- `Programme.programme_type` discriminates academic/AI Bootcamp in one shared table; `school_id`/`department_id`/`category_id` are all nullable.
- `Programme` has **no** `fee` column (academic pricing stays on `School.fee`); AI Bootcamp pricing lives exclusively on `ProgrammeMode.fee_amount` (nullable `NUMERIC(10,2)`) and `ProgrammeMode.start_date` (nullable `DATE`) — both NULL-as-sentinel, never a stored "Contact Admissions" string.
- `Application.reference_code` is a separate unique column, generated by `app/utils/reference_code.py` (date + random suffix), never derived from the sequential `id`.
- `Application.application_type` (`scholarship`/`general`/`programme_inquiry`, default `scholarship`) and `.status` (`submitted`/`under_review`/`offered`/`enrolled`/`rejected`/`withdrawn`) are enforced via `CHECK` constraints, matching Step 2's VARCHAR+CHECK typing exactly (not native enums).
- `AdminUser` has no `role`/`permissions` column.

### Relationships

`School` 1:N `Department`, 1:N `Programme` (direct). `Department` 1:N `Programme`. `ProgrammeCategory` 1:N `Programme` (AI Bootcamp only). `Programme` 1:N `ProgrammeMode`/`ProgrammeFAQ`/`ProgrammeFeature`, 1:N `Application`, 1:N `Alumni` (nullable FK). `Applicant` 1:N `Application`. `Application` N:1 `Applicant`/`Programme`, nullable N:1 `ProgrammeMode`. `GraduateProfileRequest`, `PartnerEnquiry`, `ContactMessage`, `NewsletterSubscriber`, `AdminUser` are standalone (no FKs), matching Step 2 §29's ERD exactly.

### Flask architecture confirmation

Application factory pattern (`create_app()` in `app/__init__.py`); central `extensions.py` holding unbound `db`/`migrate`; environment-variable-only config (`app/config.py`, no hardcoded secrets, dev/testing/production classes); 5 blueprints registered (`public`, `admissions`, `alumni`, `enquiries`, `admin`) — only `public` has a real route (`GET /api/health`); service-layer placeholder files present for future routes-→-services-→-models layering; `app/utils/security.py` wraps Werkzeug's `generate_password_hash`/`check_password_hash` (no login route/session/token system built); `app/utils/errors.py` registers centralized 400/404/409/500 JSON handlers app-wide, never leaking stack traces.

### Testing

18 tests across `tests/test_app_factory.py`, `test_health.py`, `test_config.py`, `test_models_import.py` — app creation, blueprint registration, error-handler registration (and a live 404 JSON-shape check), the health endpoint, config resolution across all three environments, absence of hardcoded credentials, and full model-registry/shape verification (exact 15-model set, correct table names, no forbidden models, nullable pricing fields, unique reference code, no role column on AdminUser).

```
18 passed in 0.15s
```

No live PostgreSQL server was used or required — `TestingConfig` points at an in-memory SQLite URI solely so Flask-SQLAlchemy can initialize; no test calls `db.create_all()` or issues a query. `python -m compileall` passed clean across the whole project.

### Database status

**No live database was created, connected to, or populated.** `flask db init` was run once to scaffold `migrations/` (`env.py`, `script.py.mako`, `alembic.ini`, empty `versions/`) — this only writes local files and does not require or attempt a database connection. No `flask db migrate` (autogenerate) or `flask db upgrade` (apply) was run; `migrations/versions/` is empty. No table exists anywhere. No seed data was inserted. `grep` confirms zero `db.create_all()` calls and zero `db.session` usage anywhere in the codebase.

### Frontend status

**Nothing in `build10/` was changed by Step 3.** No existing form (`apply.html`, `alumni.html`, `graduate-hire.html`, `partner-with-us.html`, `corporate-training.html`, `contact.html`, the 10 newsletter forms, `ai-bootcamp.html`) was touched, rewired, or pointed at the new backend. The existing `fetch()` call to `germaineinstitute.com/application/clients/add` in `apply-wizard.js` is untouched.

### Deferred items (explicitly out of scope for Step 3)

Public catalogue API routes, admissions/alumni/enquiries CRUD routes, admin authentication/session handling, service-layer logic implementations, generating and running the first Alembic migration, seeding any data, `application_documents`/`graduates`/`employers`/`admin_activity_log` tables and the `role` column on `AdminUser` (all Phase 3/4 per Step 2 §35), rewiring any frontend form.

---

## Final Stop

Per your Final Stop Condition: this is where work stops. No database has been created or populated, and no further step (generating/running migrations, building CRUD APIs, wiring the frontend to this backend) will begin until you review this report and explicitly authorize it.
