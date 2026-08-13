# Germaine Training Institute — Step 7 Completion Report

**Date:** August 11, 2026. Scope: complete the remaining Step 6 integrations (catalogue, alumni mapping, scholarship wizard, AI Bootcamp inquiry, CORS) and build the secure staff admin dashboard, without redesigning the public site or changing the database schema.

---

## A. Completed Integrations

- **Academic school/programme catalogue** — `assets/js/school-page.js` now refreshes each school's programme table from `GET /api/programmes?school=<slug>` before first render, on the 16 real school-family pages (9 active schools, 5 legacy/short-course schools, 2 more short-course-style pages). Falls back silently to the existing static `school-data.js` rendering if the API is unreachable or returns nothing — the existing table markup, columns, badge styling, and department filter are all reused unchanged.
- **`level_class` exposed on `GET /api/programmes`** — a small, additive backend completion (see E) needed so the catalogue bridge can preserve the exact existing badge colors.
- **CORS** — a minimal, opt-in, public-API-only CORS layer was added and decided on (see B).
- **Secure staff admin dashboard** — full authentication, authorization, and read/status-update interface over Applications, Scholarship Applications, Alumni, Contact Enquiries, Graduate Requests, Partnerships, Corporate Training, and Newsletter Subscribers. See the dedicated ADMIN DASHBOARD section below.

## B. Decisions Made

**Alumni programme field (§39 F) — SCHEMA DECISION REQUIRED, not resolved.** Re-inspected Step 2 §11/§28: `alumni.programme_id` is the only relationship the approved schema gives this record, and the `alumni` table has no `school_id` or any other school-level column. The frontend's "Programme Studied" field only ever collects a school name. There is no existing, safe mechanism in the approved schema to represent this correctly — mapping a school name to an arbitrary programme row would violate "never associate an alumnus with a random programme merely to satisfy a foreign key." No schema change was made. The alumni registration integration (already wired in Step 6) continues to omit `programme_id` entirely; the admin Alumni detail view states this openly rather than guessing (see 14J). **Decision required from you:** add a `school_id` column to `alumni`, repurpose `programme_id`, or another approach — this remains open.

**Scholarship application wizard (`apply.html`) — BLOCKED, not migrated.** Compared every field `apply-wizard.js` collects against `POST /api/admissions/applications`. Every field maps cleanly **except one, required, field: "Mode of Study"** (Full Time / Part Time / Virtual-Distance / Talented Student — `state.mode`/`modeLabel`). This is collected from every applicant and cannot be skipped (Step 1 validation blocks progression without it), but no column anywhere in the approved 15-table schema represents it. `applications.admin_notes` was considered and rejected as a place to put it — that column is explicitly documented as "internal only, never public," and silently repurposing it to capture required applicant-submitted data would misrepresent the schema rather than honestly extend it. Per your own instruction ("If a required field cannot be represented: STOP and document the exact mismatch... do not invent database fields"), the wizard was **not** migrated. `apply.html` and `apply-wizard.js` are untouched; the existing external endpoint (`germaineinstitute.com/application/clients/add`, Step 2 §39 item E) remains exactly as it was.

**AI Bootcamp inquiry form (`ai-bootcamp.html` `#aiApplyForm`) — BLOCKED, not wired.** `POST /api/admissions/applications` does structurally support `application_type="programme_inquiry"` (a real, tested enum value). However, `programme_id` is a required field on that endpoint, and this form's hidden `programme` input is only populated when a visitor arrives via a specific course's "Apply" link carrying `?course=<slug>` in the URL (`assets/js/ai-bootcamp.js` lines 147-183). The form is also reachable generically (hero CTA, nav link to `#aiApply`) with **no programme pre-selected and no in-form programme selector** — in that path there is no way to populate a required field without guessing one. Combined with Step 2 §39 item D still being an open architectural question (whether this lighter form should unify into `applications` at all), the form was left unwired, exactly as in Step 6.

**CORS / environment connection — resolved.** No live combined frontend+backend environment has been stood up in any step so far (the Flask app has only ever run transiently inside the sandbox for testing), so there was nothing to "verify actual need" against in a running system. The decision made: CORS support was added but kept fully **opt-in** (`CORS_ALLOWED_ORIGINS` env var, empty by default) and scoped only to `/api/...` — never `/admin/...`. With it unset (the default), the app behaves exactly as before Step 7: no `Access-Control-Allow-*` headers at all, i.e. same-origin only. No wildcard is ever used; no credentials header is ever sent. This gives whoever deploys the site a single, safe switch to flip if the static frontend ever ends up on a different origin from the Flask API, without any code change and without weakening the admin portal's same-origin-only session cookie.

## C. Files Created

**Backend (`germaine-backend/`):**
`app/utils/csrf.py`, `app/utils/auth.py`, `app/utils/cors.py`, `app/services/admin_service.py`, `app/cli.py`, `app/templates/admin/base.html`, `login.html`, `dashboard.html`, `_pagination.html`, `applications_list.html`, `application_detail.html`, `alumni_list.html`, `alumni_detail.html`, `contact_list.html`, `contact_detail.html`, `graduate_requests_list.html`, `graduate_request_detail.html`, `partner_enquiries_list.html`, `partner_enquiry_detail.html`, `newsletter_list.html`, `app/static/admin/admin.css`, `tests/test_admin_dashboard.py`, `tests/test_cors.py`.

**Frontend:** none (Step 7 reused Step 6's `assets/js/api-client.js`; no new frontend files were needed).

## D. Files Modified

**Backend:**
- `app/blueprints/admin/routes.py` — rewritten from an empty Step 3 placeholder into the full admin portal's routes.
- `app/config.py` — added session-cookie security settings (HttpOnly, SameSite=Lax, Secure outside dev, 8-hour lifetime).
- `app/__init__.py` — `admin_bp` re-mounted at `/admin` (was `/api/admin`, an unused empty placeholder — see rationale in `routes.py`'s docstring); registered CORS and CLI setup.
- `app/services/programme_service.py` — added `level_class` to `programme_to_dict()` output (see E).
- `.env.example` — documented the new `CORS_ALLOWED_ORIGINS` variable.
- `API_DOCS.md` — documented the `level_class` addition.
- `tests/_helpers.py` — added `create_admin_user`/`login_admin`/`get_csrf_from` helpers; added `level_class` to the seeded academic programme fixture.
- `tests/test_api_catalogue.py` — added a test asserting `level_class` is now serialized.

**Frontend:**
- `assets/js/school-page.js` — the bottom "INIT" block was made to try an API refresh of the current school's programme rows before the first render (see A). No render function, filter logic, or markup was changed.
- 11 HTML pages received one added `<script defer src="assets/js/api-client.js"></script>` tag each (nothing else changed): `courses-computing-it.html`, `courses-agriculture.html`, `courses-hospitality-tourism.html`, `courses-health-sciences.html`, `courses-engineering-technology.html`, `courses-cosmetology-fashion-design.html`, `courses-languages.html`, `courses-short-courses.html`, `courses-mass-communication-journalism.html`, `courses-business-commerce.html`, `courses-virtual-learning.html`. (5 more school pages already had it from Step 6.)

## E. Backend Changes

**Yes, the backend was changed**, in two bounded ways:
1. A new, fully protected admin portal (routes, service layer, templates, CSS, auth, CSRF) — entirely additive, reuses the existing 15 models, adds no new tables.
2. `programme_to_dict()` now serializes the pre-existing `level_class` column. This column already existed in the schema (Step 2 §28) and was already populated by the Step 4 seed script for every academic programme — it simply wasn't included in the Step 5 API response. No column, migration, or seed change was needed to add it to the response.

No other service, model, or public endpoint's behavior changed.

## F. Database Changes

```
Schema changes: NONE
Migration changes: NONE
Seed changes: NONE
```

The real Postgres instance stood up in Step 4 (15 schools, 353 programmes) was not touched in this step. `admin_users` already existed as an empty table from Step 4's schema (never seeded, per that step's own scope) — Step 7 adds a `flask create-admin` CLI command as the only way to populate it, but running it against the real database was not performed in this pass (no first admin account has been created anywhere outside the test suite).

## G. Visual Preservation

- No CSS file in `build10/` was touched.
- No HTML content, layout, copy, class name, or component structure was changed anywhere in the public site — the only HTML edits across all of Step 7 are 11 single-line `<script>` tag insertions.
- `assets/js/school-page.js`'s existing render functions (`renderProgrammes`, `rowHtml`, `applyDeptFilter`, `initDepartments`, etc.) were not modified — only the orchestration at the bottom of the file that decides *what data* to pass into them. The catalogue bridge only ever overwrites `school.programmes` and `school.count`, and only when the API call fully succeeds with a non-empty result; every other field (hero image, intro text, fee string, careers, quick links, department descriptions) is left exactly as `school-data.js` already provides.
- Navigation re-verified frozen: `initStickyHeader()` unchanged (`ACTIVATE_AT=80`/`DEACTIVATE_AT=60`), `initNavbarTransparency()` still absent from `main.js`'s init sequence, `graduate-hire-elevate.css` has no nav-specific re-theme rules (confirmed via grep — only unrelated footer/back-to-top rules remain, as before Step 6's correction).
- The admin portal has its own separate CSS (`app/static/admin/admin.css`) and templates, never loaded by or linked from any public page — the public site's design system is untouched by the admin work.

## H. Testing Results

- `node --check` on every modified/created JS file (`school-page.js`, plus all Step 6 files re-checked for regression): **all clean.**
- `python -m compileall germaine-backend`: **clean.**
- `pytest`: **114 passed** (79 Step 5 baseline + 30 new admin-dashboard tests + 1 new `level_class` test + 4 new CORS tests), **zero regressions, zero warnings.**
- API verification: `GET /api/schools`, `/api/schools/<slug>`, `/api/programmes` (including the new `level_class` field), `/api/programmes/<slug>`, `/api/programme-categories` all covered by existing + new tests.
- Admin verification (all via the automated test suite, session-cookie driven, exactly as a browser would exercise it): login success/failure/inactive-account rejection, logout, CSRF rejection on missing/invalid tokens, every protected route redirecting an unauthenticated request (never leaking data first), applications list/search/status-filter/detail/status-update (valid and invalid status values), scholarship-filtered view, alumni list/detail (including the honest "unresolved" message, never a guess), contact/graduate-request/partner-enquiry list/detail/status-update, partnerships vs. corporate-training correctly separated by `enquiry_type`, newsletter list, dashboard stats, no password hash ever rendered in any admin page, and confirmation that the public `/api/...` routes never expose admin-only data.
- Browser/console verification: not performed — no browser tooling was available in this pass; all admin and catalogue-bridge verification was done through Flask's test client (`pytest`) and manual smoke scripts against a real in-memory-SQLite-backed app instance, not a running browser session.

## I. Remaining Issues

1. **Alumni programme mapping (§39 F)** — schema decision required from you; not resolved (see B).
2. **Scholarship wizard migration** — blocked by the "Mode of Study" field having no backend column; not resolved (see B).
3. **AI Bootcamp inquiry form** — blocked by the generic-entry-path missing a required `programme_id`, plus §39 D remaining open; not resolved (see B).
4. **AI Bootcamp catalogue pages** (the 14 `ai-course-*.html` detail pages and `ai-bootcamp-courses.html`) were **not** wired to the API in this pass. They use a separate data file/renderer (`ai-courses-data.js` + `course-detail.js`) with a materially different pricing display (per-mode fee cards, "Contact Admissions" sentinel handling) than the academic school table this step's bridge targets, and no browser was available to visually verify 14+ pages of a different template family. The read API for this data already exists and is already tested (`GET /api/programmes?type=ai_bootcamp`, `/api/programmes/<slug>`) — only the frontend wiring remains, and is recommended as a focused follow-up rather than something rushed into this pass.
5. **No first admin account exists yet anywhere outside the automated test suite.** `flask create-admin` is ready to use but has not been run against any real database (local or the Step 4 Postgres instance) — running it is a deliberate, separate action for you to take when ready, not something this pass should do unattended.
6. **CORS was configured but never exercised against a real cross-origin request** — no live combined frontend+backend environment exists yet to test it against (consistent with every prior step).

## J. Step 7 Status

```
STEP 7 COMPLETE
```

Every item in scope was either safely integrated (academic catalogue, CORS decision, admin dashboard) or explicitly resolved as **correctly blocked** with the exact technical mismatch documented rather than guessed (alumni mapping, scholarship wizard, AI Bootcamp inquiry) — which is the outcome your own instructions define as success for those three items. The one genuinely deferred *integration* (AI Bootcamp catalogue pages) is a scope decision, not a blocker, and is flagged above for a focused follow-up.

---

## ADMIN DASHBOARD

**Authentication**
- Implemented. Mechanism: Flask server-side signed session cookie (`SECRET_KEY`-based), `werkzeug.security` PBKDF2-SHA256 password hashing (reused from the Step 3 `app/utils/security.py` scaffold), generic invalid-credential messaging (never reveals whether an account exists), inactive accounts rejected, no hardcoded credentials anywhere — the only way to create an admin is `flask create-admin`, which prompts interactively for the password.

**Dashboard**
- Implemented. Statistics shown: total applications + per-status breakdown (submitted/under_review/offered/enrolled/rejected/withdrawn), scholarship/general/programme_inquiry counts, alumni total, graduate-request total + pending count, partnership + corporate-training totals, contact-message total + new count, newsletter subscriber total (active). Every number is a live `COUNT`/`filter` query against the real tables — nothing is invented or hardcoded.

**Managed Records**
```
Applications           — list, search, status filter, detail, status update
Scholarships            — same Applications table, filtered to application_type='scholarship'
Alumni                  — list, search, detail (read-only — no status column exists)
Graduate Requests       — list, search, status filter, detail, status update
Partnerships             — list, search, status filter, detail, status update
Corporate Training      — same table, filtered to enquiry_type='corporate_training'
Contact Enquiries       — list, search, status filter, detail, status update
Newsletter Subscribers  — list, search, active/inactive filter (read-only)
```

**Security**
- Protected routes: every `/admin/*` route except `GET`/`POST /admin/login` requires an authenticated session; unauthenticated requests are redirected to login, never shown data first (verified by test).
- Protected APIs: none of the admin functionality is exposed as a separate public JSON API — it is entirely server-rendered pages behind the same session check, so there is no `/api/admin/*`-style surface to accidentally leave open.
- Password hashing: PBKDF2-SHA256 via Werkzeug, never plaintext, never logged.
- Session security: HttpOnly + SameSite=Lax always; Secure (HTTPS-only) in every environment except local development/testing (no local TLS).
- CSRF protection: a per-session random token, required and validated on every state-changing POST (login, logout, every status update); mismatched or missing tokens are rejected with 403.
- Authorization: enforced entirely server-side via the `admin_required` decorator — never relies on hiding a URL or on frontend-only checks.

**Database**
- No schema changes were required. `admin_users` already existed (Step 2/Step 4); every other admin-viewed table already existed. See section F above.

**Testing**
- 30 new tests in `tests/test_admin_dashboard.py` plus 4 in `tests/test_cors.py`, covering: login success/failure (wrong password, unknown email, inactive account), missing-CSRF rejection, logout + post-logout access denial, every protected route's redirect behavior, no-data-before-redirect leakage check, Applications list/search/status-filter/detail/404/status-update (valid + invalid status + bad CSRF), Scholarships view filtering, Alumni list/detail including the honest unresolved-mapping message, Contact/Graduate-Request/Partner-Enquiry list/detail/status-update, Partnerships vs. Corporate Training separation, Newsletter listing, dashboard stat accuracy, no password-hash leakage across every admin page, and confirmation the public API never exposes admin data. All 114 backend tests pass (0 regressions from the Step 5 baseline of 79).

---

## K. CMS / CONTENT MANAGEMENT

Extends the admin dashboard built above with a **structured** CMS — administrators fill in values for a fixed, code-defined set of fields and manage real News articles; they never touch HTML/CSS/JS/layout/navigation, and there is no free-form page builder anywhere in this feature.

**Website Content**
- Implemented as a single registry, `CONTENT_FIELD_REGISTRY` in `app/services/cms_service.py` — 14 fields grouped into Homepage, About Us, Student Life, and Contact Information, each mapped to text that genuinely already exists on the corresponding public page today (no invented sections). Stored in one new `site_content` table (`content_key` unique, `value` text). The admin editor (`/admin/content`) renders one form covering every registry field; saving a field blank simply deletes its override — the public page reverts to its original static wording. Nothing in this feature can create a new field; the registry is enforced at the service layer (`set_content_value` raises `ValidationError` for any key not in the registry — covered by `test_set_content_value_rejects_unknown_key`).
- **Frontend bridges wired in this pass:** homepage hero badge/headline/subtitle (`index.html`), About Us Vision/Mission/Core Values (`about.html`), Student Life hero paragraph (`campus.html`), and Contact Information — phone/email/WhatsApp/address/hours — fanned out to the hero "contact hub" icons and the Quick Contact cards on `contact.html`. Every bridge script (`homepage-cms-bridge.js`, `about-cms-bridge.js`, `student-life-cms-bridge.js`, `contact-info-cms-bridge.js`) follows the same rule already established for the Step 7 catalogue bridge: fetch, overwrite only the specific element whose CMS value is non-empty, `.textContent` only (never `innerHTML` on admin-supplied text, so nothing here can inject markup), and silently keep the existing static wording on any network failure, timeout, or absent value.
- **Deliberately deferred, not abandoned:** the homepage hero photo slideshow and the Student Life Clubs/Sports repeating lists. `content_list_items` (see Database below) fully supports all three as a `list_key`, and the admin portal can create/edit/reorder/archive items in all three today (`/admin/content/lists/<list_key>`) — but `hero-template.js`, `clubs-showcase.js`, and `campus-gallery.js` each perform their own synchronous slideshow/dot/arrow initialization on page load, the same defer-script timing risk already documented and solved once for `school-page.js` in Step 7's catalogue integration. Swapping slide DOM after that initialization runs without first tracing each script's internals in a real browser would risk desyncing the dots/arrows/autoplay — not something to guess at without visual verification. Flagged as a focused follow-up, exactly like the Step 7 AI Bootcamp catalogue pages were.

**News**
- Real CRUD: create (as a draft), edit, publish, unpublish (back to draft), archive — backed by a new `news_articles` table (`slug` unique, `title`, `summary`, `body`, `category`, `author`, `featured_image_id` FK to `media_assets`, `status` CHECK IN draft/published/archived, `published_at`, `created_by_id`). Publishing requires both a title and a body (`test_news_publish_requires_title_and_body`); slugs auto-generate from the title with a numeric suffix on collision (`test_news_two_articles_same_title_get_distinct_slugs`).
- `news.html`'s 6 existing static cards were **not** auto-migrated — confirmed deliberately absent from any seed or migration. `assets/js/news-cms-bridge.js` fetches `GET /api/news` and replaces `#newsGrid`'s contents only when at least one published article exists; with zero published articles (the default state until an admin actually publishes something) the 6 static cards are untouched.
- **New page: `news-article.html`** — no article detail page existed anywhere in the project before this addition, and a "Read More" link on a real article needs somewhere to go. Built as a literal copy of `news.html`'s head/nav/footer/scripts (guaranteeing pixel-identical chrome and zero navigation drift) with only the page-header and content-grid section replaced by a single article-detail block, reusing existing typography classes (`.news-content`, `.container`) rather than introducing new CSS. `assets/js/news-article-detail.js` reads `?slug=` from the URL, calls `GET /api/news/<slug>`, and renders it; a missing/unpublished/nonexistent slug shows a plain "Article Not Found" message with a link back to `news.html` — never a raw error.

**Media Library**
- New `media_assets` table (`filename`, `original_filename`, `url_path`, `alt_text`, `mime_type`, `size_bytes`, `width`/`height` nullable, `status` CHECK IN active/archived, `uploaded_by_id`). Upload validation is three-layered and enforced in `cms_service.validate_upload()`: file extension must be in an allow-list (`.jpg .jpeg .png .gif .webp`), the browser-declared `Content-Type` must be an image type, and the file's first bytes are sniffed against real magic-byte signatures for each format — all three must agree, or the upload is rejected with a specific reason (`test_media_upload_rejects_disguised_executable` uploads a `.php` payload disguised with a `.png` extension and confirms it is rejected, not silently accepted). Files are never stored under the browser-supplied name — `generate_safe_filename()` always produces a random `uuid4` token plus the validated extension, stored under `app/static/media/` (Flask's own static folder, never executed as code). No image-processing library (e.g. Pillow) was added — the project's dependencies were kept deliberately minimal per the original Step 3 scaffold instruction, so `width`/`height` remain nullable and unpopulated rather than pulling in a new dependency for it.
- Replace-in-place is supported (`/admin/media/<id>/replace`) — the existing `MediaAsset` row's `id` is preserved so every reference to it (a News article's featured image, a content-list item's image) automatically shows the new file without needing to re-point anything; the old physical file is best-effort deleted (never fatal if that fails).
- Archive (not permanent delete) is the only removal path, consistent with the codebase-wide draft/unpublish/archive preference.

**Academics**
- Thin, additive update functions over the **existing** Step 2 catalogue tables — no new academics tables. `update_school()` edits `School.description`/`fee`/`is_active`/`display_order`; `update_programme()` edits overview/gain-points/entry-requirement/exam-body/apply-heading/apply-subtext/is_active/display_order and has **no `fee` parameter at all**; `update_programme_mode()` edits AI Bootcamp per-mode `fee_amount`/`is_available`/`schedule`. The two pricing models are kept strictly separate exactly as Step 2 §8 requires: academic flat fee is only ever reachable through `update_school()`, AI Bootcamp per-mode fee only through `update_programme_mode()` — `test_academics_programme_update_never_touches_fee` asserts a `fee` value posted to the programme-edit form is silently ignored because the underlying function has no such parameter to receive it. `update_category()` edits an AI Bootcamp category's label/icon (slug is fixed, since programme links already reference it).
- No public catalogue frontend pages were touched in this pass — this is an authenticated-admin editing surface over data the public API already serves.

**Database**
```
4 new tables (additive only, zero changes to the existing 15):
  media_assets        — see Media Library above
  news_articles        — see News above
  site_content         — see Website Content above
  content_list_items   — one generic table (list_key CHECK IN
                          homepage_hero_slides / student_life_clubs /
                          student_life_sports), used instead of three
                          near-duplicate tables — same normalization
                          reasoning already applied to
                          partner_enquiries.enquiry_type in Step 2 §15.
Model registry: 15 Step-2 baseline + 4 CMS = 19 (test_models_import.py
  asserts the 15 are unchanged and the full set is exactly these 19).
Migration: 2ac3535209b9 (generated by `flask db migrate`, reviewed
  column-by-column against all 4 model definitions before applying,
  then applied via `flask db upgrade` against the real local Postgres
  instance and verified: pre-existing data untouched — 15 schools, 353
  programmes, all counts identical before and after — and all 4 new
  tables created empty with their CHECK constraints intact).
```
Every new model's own file carries a full "CMS SCHEMA CHANGE REQUIRED" docstring block (Entity/Reason/Fields/Relationship/Why existing schema cannot support it/Impact), as required.

**Security**
- Reuses the existing admin session/CSRF/authorization machinery exactly — no parallel auth system. Every CMS admin route requires the same authenticated session (`admin_required`) and validates the same per-session CSRF token on every POST, including the multipart file-upload routes (`test_media_upload_without_csrf_token_is_rejected`).
- All CMS write access lives under `/admin/...`, never under `/api/...` — the public read endpoints (`GET /api/news`, `/api/news/<slug>`, `/api/site-content`, `/api/content-lists/<key>`) are read-only, unauthenticated, and expose nothing beyond what the registries deliberately allow (`test_public_cms_endpoints_never_require_authentication`, and the media grid renders `url_path` only, never a server filesystem path — `test_media_asset_never_exposes_filesystem_path_in_admin_html`).
- Sanitization: all admin-entered text is stored and rendered as plain text (Jinja's autoescaping in templates, `.textContent` in every frontend bridge) — no rich-text/HTML field exists anywhere in this CMS, so there is no script-injection surface to sanitize against in the first place.
- Backward-compatible-by-construction: every public CMS read path (`get_content_value`, `list_list_items`, `list_published_news`) returns `None`/an empty list rather than raising when nothing has been entered yet — confirmed by `test_public_news_list_empty_by_default`, `test_public_site_content_ignores_unrecognized_keys`, and `test_public_content_list_empty_for_unrecognized_key_not_an_error`. An empty CMS never blanks a public page.

**Testing**
- 34 new tests in `tests/test_cms.py`: CMS-route authentication/authorization, Website Content save + registry rejection, Content List Items create/update/archive + max-items enforcement, Media upload success/rejection (disguised executable, disallowed extension)/alt-text/replace/archive/no-filesystem-path-leak, News full lifecycle (draft → publish → unpublish → archive) + publish-requires-body + slug-collision handling, Academics school/programme/programme-mode/category updates (including the fee-separation guarantee), and the full public read API (news list/detail, site-content, content-lists) including the "never require authentication" and "empty CMS is not an error" guarantees.
- Full regression: **149 passed, 0 failed** (115 Step 7 baseline + 34 new CMS tests) — `python -m pytest` from `germaine-backend/`.
- `node --check` on all 6 new/modified frontend JS files (`homepage-cms-bridge.js`, `about-cms-bridge.js`, `student-life-cms-bridge.js`, `contact-info-cms-bridge.js`, `news-cms-bridge.js`, `news-article-detail.js`) plus a full-repo `node --check` sweep: all clean.
- HTML tag-balance check (div/section/article/header/footer/nav/main/ul/li/form open vs. close counts) on every touched page (`index.html`, `about.html`, `campus.html`, `contact.html`, `news.html`, `news-article.html`): all balanced.
- Every new/edited element ID referenced by a bridge script was cross-checked against its target HTML file to confirm it exists exactly once (no silent no-op due to a typo'd selector).
- Browser/console verification: not performed, for the same documented reason as the rest of Step 7 — no browser tooling is available in this environment. All verification here was via Flask's test client, Node's own JS syntax checker, and static cross-referencing, not a rendered browser.

---

**Step 7 (including the CMS addition) is complete as scoped above.** Automated verification (149/149 backend tests, full JS syntax and HTML-balance sweep) is as far as this environment can confirm without a real browser — the honest limitation is carried into Step 8 below rather than glossed over. Step 8 (Full System Testing, Refinement, Consistency & Quality Assurance) begins next, using the same test-client-and-static-analysis approach, with that constraint stated up front in its own report.
