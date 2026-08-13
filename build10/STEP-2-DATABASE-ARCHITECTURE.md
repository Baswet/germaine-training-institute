derer# Germaine Training Institute — Step 2: Database Architecture & Data Model

**Date:** August 11, 2026. **Design only.** No database, tables, SQL, models, migrations, APIs, or frontend/CSS/JS changes were created. Every entity below is justified against the actual, verified frontend (Step 0.5) — nothing is speculative.

---

## 1. Executive Summary

This design is built entirely from what the Step 0.5 verification confirmed exists: 7 real forms, one genuinely structured AI Bootcamp data file (`ai-courses-data.js`, 14 courses with per-mode pricing), one genuinely structured academic data file (`school-data.js`, 4,313 lines, 15 schools/9 active with a real-but-partial Department layer), and zero file uploads, zero live News/Vacancies persistence needs, and one unconfirmed external endpoint that this design does not depend on.

The result is **15 tables across Phase 1 and Phase 2: 14 Phase 1 tables plus 1 Phase 2 admin table** (`admin_users`), with 3 more identified and deliberately deferred to Phase 3/4 with reasons — not built speculatively. AI Bootcamp and Academic programmes share one `programmes` table (they're both "a thing you can apply to"), but their pricing models are kept genuinely distinct per your instruction #3: academic fees stay a flat per-school value, AI Bootcamp fees stay per-learning-mode — the schema does not force one shape onto the other.

---

## 2. Verified Database Scope

Confirmed in scope (real forms/data exist): Schools, Departments (partial), Programmes (academic + AI Bootcamp, unified), Programme Learning Modes, Programme FAQs, Programme Features, Applicants, Applications, Alumni, Graduate Profile Requests, Partner Enquiries, Contact Messages, Newsletter Subscribers, Admin Users.

Confirmed **out of scope** for this design, per your explicit instructions: News, Vacancies, `gallery-2026`, `hero-template.html`/`course-detail.html`, static institutional content, application document storage (deferred to Phase 3), a public Graduates directory (no frontend submission path exists — deferred), complex RBAC (deferred).

---

## 3. Domain Architecture

| Domain | In this design? | Why |
|---|---|---|
| A. Academic / Programmes | Yes | `school-data.js` is real, structured, already live |
| B. Admissions | Yes | `apply.html` is a real, real-field, multi-step form |
| C. Scholarships | **Merged into Admissions** — `apply.html` *is* the scholarship application; there is no second, separate scholarship flow anywhere in the frontend | See §9 |
| D. AI Bootcamps | Yes — **reuses the Programmes table**, with its own `programme_modes` child data | See §6 |
| E. Alumni | Yes | `alumni.html` is real |
| F. Graduates / Employers | Partial — the *request* is real (`graduate-hire.html`); a self-service Graduate directory is not (no submission path exists) | See §12 |
| G. Partners | Yes | `partner-with-us.html` and `corporate-training.html`'s consultation form share one shape | See §13 |
| H. Communication | Yes | Contact + Newsletter both have real, currently-unwired forms | See §14 |
| I. Vacancies | **Excluded**, per your instruction — 6 static jobs, Apply Now already correctly routes to `contact.html`, no frontend justifies a jobs table | See §16 |
| J. News | **Excluded**, per your instruction — 6 static articles, no growth mechanism, no compelling reason found | See §17 |
| K. Administration | Yes, minimal | One admin role is sufficient for Phase 1/2 | See §18-19 |

---

## 4. Entity Decision Matrix

| Entity | DB Required? | Reason | Priority |
|---|---|---|---|
| Schools | **Yes** | `school-data.js` is real, structured, drives 15 live pages | Essential |
| Departments | **Yes (partial)** | Real for 4 of 9 active schools (`departments[]` in the actual data); the other 5 have none — schema must allow zero departments, not require them | Essential |
| Programmes (academic) | **Yes** | 339 real programme entries currently in `school-data.js` | Essential |
| Programmes (AI Bootcamp) | **Yes** | 14 real course objects in `ai-courses-data.js` | Essential |
| Programme Categories (AI) | **Yes** | Real filter pills on the AI catalogue hub, backed by real `category`/`categoryLabel` fields | Essential |
| Programme Modes | **Yes** | Directly drives the existing pricing cards — confirmed dynamically rendered today | Essential |
| Programme FAQs | **Yes** | Confirmed dynamically rendered (`renderFaqs`) | Essential |
| Programme Features ("What's Included") | **Yes** | Confirmed dynamically rendered into the pricing-card checklist (`course.format`) | Essential |
| Programme "Gain" points | **Yes, as a JSON field on `programmes`, not a table** | Confirmed dynamically rendered, but it's a flat list of strings with no independent attributes — a table would be over-normalization | Essential |
| Programme Careers (`careers` field) | **No, not in this design** | Confirmed in Step 0.5 to be dead-in-JS / only live via static hand-authored HTML — no dynamic renderer touches it today | Not included — see §26 |
| Programme Skills / detailed Projects | **No** | Confirmed dead data — defined in `ai-courses-data.js`, rendered nowhere | Excluded entirely |
| Applicants | **Yes** | `apply.html` collects real personal data | Essential |
| Applications | **Yes** | Real multi-step form, real fields | Essential |
| Application Documents | **No — Phase 3, not MVP** | Zero file-upload fields exist in the current frontend | Future |
| Alumni | **Yes** | `alumni.html` is real | Essential |
| Graduate Profile Requests | **Yes** | `graduate-hire.html`'s `gpForm` is real | Essential |
| Graduates (directory) | **No — Phase 3/4** | No frontend path for a graduate to submit/claim a profile exists yet | Future |
| Partner Enquiries | **Yes** | `partner-with-us.html` + `corporate-training.html` both real | Essential |
| Contact Messages | **Yes** | `contact.html` is real (though currently unwired) | Essential |
| Newsletter Subscribers | **Yes** | 10 real (unwired) forms | Essential |
| Admin Users | **Yes** | Needed for any dashboard at all | Essential (Phase 2) |
| Admin Roles (multi-role RBAC) | **No — Future** | One role is sufficient today; nothing in the frontend implies multiple staff permission tiers yet | Future |
| Audit Log | **No — Phase 3/4** | Reasonable once real staff are editing real records, not needed to launch | Future |
| Vacancies | **No** | Per your instruction — static, Apply Now already has a working (if generic) destination | Excluded |
| News | **No** | Per your instruction — static, no compelling reason | Excluded |
| Gallery-2026 / legacy pages | **No** | Per your instruction — not a backend concern | Excluded |

---

## 5. Final Entity List

**Phase 1 — 14 tables**

1. `schools`
2. `departments`
3. `programme_categories`
4. `programmes`
5. `programme_modes`
6. `programme_faqs`
7. `programme_features`
8. `applicants`
9. `applications`
10. `alumni`
11. `graduate_profile_requests`
12. `partner_enquiries`
13. `contact_messages`
14. `newsletter_subscribers`

**Phase 2 — 1 additional table**

15. `admin_users`

**Final total: 15 tables total = 14 Phase 1 + 1 Phase 2** — not the 12 estimated in the earlier (pre-verification) backend plan. The difference is entirely the Academic/AI Bootcamp programme structure turning out to be real and richer than first assumed (`programme_categories`, `programme_modes`, `programme_faqs`, `programme_features` didn't exist as distinct concepts in the earlier plan because the earlier plan hadn't yet found `school-data.js` or fully traced `ai-courses-data.js`). Full reconciliation in §37. This same 14 Phase 1 + 1 Phase 2 = 15 total split is used consistently everywhere this count is referenced in this document (§33-34, §38).

---

## 6. Academic Data Model

```
schools (15 rows: 9 active + 6 legacy-kept-for-bookmarks)
   │  fields include a single flat `fee` — see §8
   │
   └──< departments (0-3 rows; only hospitality/engineering/cosmetology/business have any)
            │
            └──< programmes (via department_id, when present)
   │
   └──< programmes (directly, via school_id, when the school has no departments)
```

**Direct migration source:** `assets/js/school-data.js` (verified: `count` field matches `programmes.length` exactly for all 15 entries — the data is internally consistent and safe to migrate as-is). One `programmes` table serves both department-attached and school-direct programmes: `department_id` is nullable; a programme has either a `department_id` (department-based schools) or just a `school_id` (flat schools) — never both required.

**Career links & quick links:** kept as JSON columns (`careers` on `schools`/`departments`, `quick_links` on `schools`/`departments`) rather than separate tables — see §26 for why.

---

## 7. AI Bootcamp Data Model

```
programme_categories (ai, software-engineering, cyber-security, data-analytics,
                       cloud-computing, python-programming, ui-ux-design,
                       high-school-bootcamp, ai-for-business — the real, currently-used category values)
   │
   └──< programmes (programme_type = 'ai_bootcamp', category_id set)
            │
            ├──< programme_modes (1-3 rows: Full-Time Hybrid / Full-Time Remote / Part-Time Remote)
            ├──< programme_faqs
            └──< programme_features ("What's Included" — from `course.format`)
```

**This is the same `programmes` table as Academic** (§6) — not a duplicate system, per your instruction #1. A `programme_type` column (`'academic'` | `'ai_bootcamp'`) distinguishes them, and `school_id`/`department_id` are simply left `NULL` for AI Bootcamp rows (they don't belong to an academic school in the current data — confirmed, `ai-courses-data.js` has no school reference at all, only `category`).

**Direct migration source:** `assets/js/ai-courses-data.js`'s 14 course objects → `programmes` rows (`programme_type='ai_bootcamp'`), their `modes` arrays → `programme_modes` rows, their `faqs` arrays → `programme_faqs` rows, their `format` arrays → `programme_features` rows, their `gain` arrays → the `programmes.gain_points` JSON column.

**Confirming your requirement directly:** the existing pricing cards read, per mode: label/sub (Full-Time Hybrid, etc.), duration, start_date, fee, schedule, and a computed "What's Included" checklist from features. Every one of those is a column on `programme_modes` or `programme_features` below (§27, §14 requirement checklist). Nothing about the card's visual design needs to change — this schema is built to feed the *existing* renderer, not replace it.

---

## 8. Programme Pricing & Intake Model — Explained (your instruction #3)

**The two pricing models are genuinely different shapes, confirmed in Step 0.5, and this schema keeps them separate rather than forcing a fit:**

- **Academic programmes:** one flat `fee` value lives on the **`schools`** table (verified: `school-data.js` has exactly one `"fee"` string per school, e.g. `"KES 11,500"` — not per programme, not per mode). A `programmes` row for an academic programme has **no fee of its own** — its price is whatever the parent school's flat fee is. This is a direct, honest reflection of what the data actually contains today; it is not this design inventing a simplification.
- **AI Bootcamp programmes:** each `programme_modes` row has its **own** `fee_amount` (nullable — see below) — genuinely different per Full-Time Hybrid / Full-Time Remote / Part-Time Remote, confirmed by the real, distinct KSh values in `ai-courses-data.js`.

**Historical pricing:** not designed in for Phase 1 — nothing in the current frontend shows or needs price history, and adding `programme_fee_history` now would be exactly the "over-engineering" your instructions warn against. If an admin ever needs to change a fee, updating `programme_modes.fee_amount` (or `schools.fee`) directly is sufficient; add a history table later only if a real reporting need appears.

**"Contact Admissions" handling:** rather than storing the literal string "Contact Admissions" in a numeric column, `fee_amount` is nullable — `NULL` means "Contact Admissions," exactly matching the current JS default behavior (`pricing.hybridFee || "Contact Admissions"`). The application layer (not the database) is responsible for the display string, matching how the current renderer already does it.

**Admin editability, without touching HTML:** once seeded, an admin changing `programme_modes.fee_amount` or `schools.fee` (via the future Phase 2 dashboard) changes what the live pricing cards show — no HTML edit required. This directly satisfies "the system should eventually allow an administrator to change a fee without changing HTML."

---

## 9. Admissions / Application Model

```
applicants
   │
   └──< applications ──> programmes (the chosen programme)
                     ──> programme_modes (nullable — set only when the chosen
                                           programme actually has modes, i.e.
                                           AI Bootcamp; NULL for academic)
```

**One applicant, many applications over time** — chosen deliberately: nothing in the frontend prevents someone applying to more than one programme, or reapplying in a future intake, and an applicant record (name/email/phone/national ID/etc.) shouldn't be re-collected every time. **Matching wording correction:** applicants are matched primarily by their **unique email address** (`applicants.email` is `UNIQUE`, §28) on each new submission — an existing row is reused if the email matches, otherwise a new one is created. Phone is retained as an additional identifying/contact field on the record, not a second matching key — there is no composite email+phone uniqueness rule, and none is being introduced. This corrects an earlier wording in this section that described matching as "by email+phone," which could be read as implying a composite key that the table specification (§28) never actually defined.

**Built from `apply.html`'s real fields only** (Step 0.5 §14, re-confirmed): `full_name`, `email`, `phone`, `national_id`, `date_of_birth`, `gender`, `county`, `education_level`, `kcse_grade`, plus the selected `programme_id` and (for AI Bootcamp) `programme_mode_id`, plus `consent`. **Not** built around `https://www.germaineinstitute.com/application/clients/add` — per your instruction #4, that endpoint is treated purely as "an existing frontend submission target," not a schema dependency. This table is designed so the *new* Flask API can be the real target once built; the old `fetch()` call in `apply-wizard.js` gets replaced or pointed at the new endpoint later, outside this design step.

**A note on scope:** `ai-bootcamp.html`'s separate, lighter `aiApplyForm` (name/email/phone/programme interest only) is treated as a lightweight variant of the same `applications` entity (`application_type = 'programme_inquiry'` vs. `'full_application'` from the wizard) rather than a second table — its fields are a strict subset of what `applications` already needs to hold for the main wizard, so a second table would just be `applications` with fewer columns filled in.

---

## 10. Scholarship Model

**No separate scholarship table.** Verified in Step 0.5: `apply.html`'s own `<h1>` is literally "Apply for a Full Scholarship" — there is exactly one application flow on this entire site, and it *is* the scholarship application. Building a parallel `scholarships` table would duplicate `applicants`/`applications` for no real second flow that currently exists. If Germaine ever launches a *non-scholarship* general application later, the existing `applications.application_type` column absorbs that (`'scholarship'` vs. `'general'`) without a schema change.

---

## 11. Alumni Model

```
alumni ──> programmes (nullable FK — labelled "Programme Studied", see discrepancy note below)
```

Fields, taken directly from `alumni.html`'s real form (re-confirmed, no invented fields): `full_name`, `email`, `phone`, `programme_id` (FK — see discrepancy note below), `graduation_year`, `organisation` (optional), `engagement_interests` (JSON array — the Networking/Mentorship/Events/Career Opportunities pill selections), `consent`, `registered_at`.

**One table, not split into "registration" + "profile":** the current form collects everything about an alumnus in a single submission with no separate "build your profile later" step anywhere in the frontend — splitting it would be speculative.

**⚠ Discrepancy flagged — VALIDATION REQUIRED BEFORE SEEDING (added to §39 as item F):** re-verified directly against `alumni.html`'s markup (`<select id="aluProgramme" name="programme">`, `<label for="aluProgramme">Programme Studied *</label>`). The field is *labelled and named* as a programme selector, but its actual `<option>` values are **school names** — "School of Medical & Health Sciences," "School of Engineering," "Business & Social Sciences," etc. (9 schools) — plus one catch-all "Germaine AI Bootcamp" option. It does not list individual programmes at all. So the real frontend field is, in substance, a **School Studied** selector wearing a "Programme Studied" label, not a genuine programme-level selection. This was not caught in the original Step 2 pass, which took the field's label at face value. **No model change has been made because of this** — `alumni.programme_id → programmes.id` is left exactly as designed, per instruction #6, rather than guessing whether the correct fix is (a) renaming/repurposing the FK to `school_id`, (b) keeping `programme_id` and mapping each school-level selection to some representative/placeholder programme row, or (c) something else. This must be resolved by you before any alumni-related seed or migration decision is made.

---

## 12. Graduate & Employer Model

```
graduate_profile_requests   (Phase 1 — real, from graduate-hire.html)
        (no FK to a `graduates` table yet — see below)

graduates                    (Phase 3/4 — future, NOT built now)
```

**Why no `employers` table:** `graduate-hire.html`'s form collects employer/company/contact details **inline, per request** — there's no employer login, no repeat-employer recognition, nothing in the frontend that implies "employers" are first-class accounts. `graduate_profile_requests` simply has `employer_name`, `company`, `email`, `phone`, `role_needed`, `message` as columns — exactly what the form collects. If Germaine later wants employer accounts (so a returning employer doesn't retype their details), promote these columns into a real `employers` table then; it's a clean, low-risk migration later, not a reason to build it speculatively now.

**Why no `graduates` table yet:** confirmed in Step 0.5 — there is no frontend path for a graduate to submit, claim, or manage their own profile. A `graduates` directory would be 100% admin-entered speculative data with nothing in the current site driving it. Flagged for **Phase 3/4**, with the privacy model below ready for when it's built.

**Privacy design (ready for Phase 3/4, per your Step 2 brief's own instinct):** when `graduates` is eventually built, `graduate_profile_requests.status` (`pending` → `approved` → `fulfilled`/`declined`) gates whether any graduate detail is ever shared — an employer's request never directly queries a graduate's full record; an admin approves a request, and only then is a graduate's info released to that employer through a controlled channel. No public or employer-facing API should ever expose a raw `graduates` table.

---

## 13. Partner Model

```
partner_enquiries
```

**One table for both `partner-with-us.html` and `corporate-training.html`'s consultation form** — verified their field sets are the same shape (organisation, contact name, email, phone, an "interest/need" field, message), differing only in exact label wording ("partnership type" vs. "training need"). `enquiry_type` (`'partnership'` | `'corporate_training'`) distinguishes them without duplicating the table. No CRM-style pipeline/stage tracking added — nothing in the frontend implies one; `status` (`new` → `contacted` → `closed`) is enough.

---

## 14. Contact & Newsletter Model

```
contact_messages        (name, email, subject, message, status, submitted_at)
newsletter_subscribers  (email, source_page, consent, subscribed_at, unsubscribed_at, is_active)
```

**One `newsletter_subscribers` table for all 10 forms**, per your instruction — `source_page` records which of the 10 pages a subscriber came from (useful analytics, zero extra tables). No `name` column — verified none of the 10 instances collect one. `contact_messages` has no `phone` column — verified the real form doesn't collect one either; not adding it speculatively.

---

## 15. Corporate Training Model

**No separate table — folded into `partner_enquiries`** (§13) via `enquiry_type = 'corporate_training'`. Building a third near-identical table here would be exactly the unjustified duplication your instructions warn against.

---

## 16. Vacancy Model

**Not designed — excluded per your instruction.** Verified: 6 hardcoded jobs, Apply Now already correctly routes to `contact.html`. No table proposed. If you later want per-job applications or more than occasional manual HTML edits, revisit this in a future phase — not before.

---

## 17. News Recommendation

**Option A — remain static.** Per your instruction and the Step 0.5 finding (6 hardcoded articles, no growth mechanism, "Read More" links already point to real existing pages rather than dedicated article pages). No table proposed.

---

## 18. Admin & Authentication Model

```
admin_users (id, name, email, password_hash, is_active, last_login_at, created_at, updated_at)
```

Minimum viable, per your instruction #9 — a single implicit "admin" role for Phase 1/2 (every `admin_users` row can do everything the dashboard offers). No `role` column forced in now; see §19 for how to add one later without a breaking change.

**Password hashing:** `pbkdf2:sha256` or `bcrypt`, applied at the application layer — the database only ever stores the hash, never a plaintext password, never in a log.

---

## 19. Roles & Permissions

**Not built for Phase 1/2** — one implicit role is enough for a first admin team. **Future expansion path, if ever needed:** add a single `role` column (`VARCHAR`, e.g. `'super_admin'` | `'admissions'` | `'content'`) directly to `admin_users` — this is a additive, non-breaking change, not a reason to build a `roles`/`permissions` join-table system now that nothing in the current frontend or workflow justifies.

---

## 20. Audit Logging

**Not built for Phase 1/2.** Recommended for **Phase 3**, once real staff are editing real applicant/alumni/graduate/partner records and "who changed this and when" becomes an actual operational question — not before. When added: a single `admin_activity_log` table (`admin_user_id`, `action`, `entity_type`, `entity_id`, `metadata` JSON, `created_at`) covering login, status changes, and record edits is sufficient; no need for a table per action type.

---

## 21. File Storage Architecture

**Not built for Phase 1/2** — confirmed zero upload fields exist in the current frontend (§ per your instruction #5). Documented here only so Phase 3 has a ready answer:

| | Recommendation |
|---|---|
| Development | Local filesystem, outside the web root (e.g. `uploads/` in the Flask project, never inside `static/`) |
| Production | Object storage (S3-compatible — AWS S3, DigitalOcean Spaces, or Backblaze B2) — survives redeploys, doesn't bloat the app server's disk, easy to put behind signed/expiring URLs for sensitive documents |
| Database | **Never** the file binary itself — only metadata (`application_documents.file_path`/`storage_url`, `mime_type`, `size_bytes`, `uploaded_at`) once that table is actually built in Phase 3 |

---

## 22. Privacy & Security Model

| Data | Sensitivity | Access rule |
|---|---|---|
| `applicants` (national ID, DOB, KCSE grade) | High | Admin-only; never exposed via any public API |
| `applications` | High | Admin-only, applicant can see only their own (Phase 3, if a status-check feature is ever built) |
| `alumni` | Medium | Admin-only for full record; nothing public today |
| `graduate_profile_requests` | Medium (contains employer contact info + what they're looking for) | Admin-only |
| `partner_enquiries` / `contact_messages` | Medium | Admin-only |
| `newsletter_subscribers` | Low, but still PII (email) | Admin-only list view; no public export |
| `admin_users.password_hash` | Critical | Never returned by any API response, ever — not even to other admins |
| `schools`/`departments`/`programmes`/`programme_modes`/`programme_faqs`/`programme_features` | **Public** | These are exactly what the site already shows anonymously today |

---

## 23. Normalization Decisions

- **`careers` and `quick_links` kept as JSON columns, not tables:** both are short, fixed-shape lists (plain strings, or label+url pairs) with no independent identity, no cross-entity querying need, and no attributes beyond what's already in the array. A relational table for these would be normalization for its own sake — exactly what your instructions warn against ("do not blindly normalize every field into a separate table").
- **`programme_faqs` and `programme_features` ARE real tables**, not JSON, because they're confirmed to be dynamically rendered lists that a future admin will realistically want to add/reorder/remove individually — a genuine repeating entity, not just display data.
- **Academic fee lives on `schools`, not `programmes`:** reflects the real data shape (§8) rather than inventing a per-programme fee that doesn't exist today.
- **No duplicate applicant/employer/partner info:** `applications` references `applicants` by FK rather than repeating name/email per application; `graduate_profile_requests` intentionally does **not** yet reference a separate `employers` table (§12) since no repeat-employer pattern exists in the frontend to normalize against.

---

## 24. Primary Key Strategy

**Recommendation: auto-increment integers (`BIGSERIAL` in PostgreSQL) for every internal primary key,** plus a separate, non-sequential public identifier only where something is exposed outside the admin dashboard:

- Internal PKs (`id BIGSERIAL`): fast joins, simplest possible Flask/SQLAlchemy integration, no practical downside for a single-institution system at this scale.
- **Exception:** `applications.reference_code` (a short random/UUID-based string, separate from `id`) — if you ever want applicants to check their own status by a code, a sequential integer ID would let anyone enumerate other applicants' records by guessing numbers. A separate public reference code avoids that without giving up integer PKs everywhere else.
- `programmes.slug` and `schools.slug` (unique, human-readable — `"software-engineering"`, `"school-of-computing"`) serve the same "safe to expose in a URL" purpose for public catalogue pages, alongside (not instead of) their integer PK.

---

## 25. Slugs

| Table | Needs a slug? | Why |
|---|---|---|
| `schools` | Yes | Public school pages already use human-readable URLs (`courses-health-sciences.html` pattern) |
| `programmes` | Yes | AI Bootcamp already has real slugs today (`software-engineering`, `ui-ux-design`, etc.) — migrate as-is |
| `departments` | No | Never appears in a URL on its own — only ever shown nested under a school (`?dept=N` uses a numeric index today, not a slug) |
| Everything else | No | Never publicly addressed by name |

All slugs: `UNIQUE`, lowercase, hyphenated — matching the real values already in `ai-courses-data.js`/`school-data.js`.

---

## 26. Indexes

| Index | On | Why |
|---|---|---|
| `programmes.slug` | unique | Programme detail-page lookups |
| `programmes.school_id`, `programmes.department_id` | FK indexes | Listing a school's/department's programmes |
| `programmes.programme_type` | plain | Filtering academic vs. AI Bootcamp catalogues |
| `programme_modes.programme_id` | FK index | Loading a programme's pricing cards |
| `applications.applicant_id`, `applications.programme_id` | FK indexes | Applicant history; per-programme application counts |
| `applications.status` | plain | Admin queue filtering (the single most common admin query) |
| `applications.submitted_at` | plain | Admin sorting/date-range filtering |
| `alumni.email`, `applicants.email`, `newsletter_subscribers.email` | unique | Prevent duplicate signups; fast lookup on repeat submission |
| `admin_users.email` | unique | Login lookup |

Not indexed: rarely-queried free-text fields (`message`, `notes`, `description`) — full-text search isn't a confirmed requirement anywhere in the current frontend.

---

## 27. Status Systems

| Table | Status field | Allowed values | Who changes it |
|---|---|---|---|
| `applications` | `status` | `submitted` → `under_review` → `offered` → `enrolled` \| `rejected` \| `withdrawn` | Admin only (Phase 2 dashboard) |
| `graduate_profile_requests` | `status` | `pending` → `approved` → `fulfilled` \| `declined` | Admin only |
| `partner_enquiries` | `status` | `new` → `contacted` → `closed` | Admin only |
| `contact_messages` | `status` | `new` → `read` → `responded` | Admin only |
| `newsletter_subscribers` | `is_active` | boolean (subscribed/unsubscribed) | System (on unsubscribe link) or admin |
| `admin_users` | `is_active` | boolean | Super admin only, once multi-admin exists |

Status **changes are not separately logged** in Phase 1/2 (no `application_status_history` table) — consistent with §20 deferring audit logging; `applications.updated_at` alone is enough to know *when* the current status was last set until a real need for full history appears.

---

## 28. Complete Table Specifications

### Table: `schools`
**Purpose:** the 15 academic schools from `school-data.js` (9 currently in navigation, 6 kept for existing bookmarked pages).
| Field | Type | Required | Default | Constraints | Description |
|---|---|---|---|---|---|
| id | BIGSERIAL | Yes | auto | PK | |
| slug | VARCHAR(80) | Yes | — | UNIQUE | e.g. `"health"`, matches `school-data.js` key |
| name | VARCHAR(200) | Yes | — | | Canonical display name — flag the Business & Commerce/Social Sciences naming inconsistency (Step 0.5 §4) for you to resolve before seeding |
| description | TEXT | No | NULL | | From `intro` |
| image_path | VARCHAR(300) | No | NULL | | |
| fee | VARCHAR(50) | No | NULL | | Flat representative fee, e.g. `"KES 11,500"` — kept as a display string, not decimal, since it's shown as-is today and its exact numeric semantics (fixed vs. "from") aren't confirmed |
| is_active | BOOLEAN | Yes | true | | Whether shown in current navigation (maps to `SCHOOL_ORDER` membership) |
| display_order | INTEGER | No | NULL | | |
| careers | JSON | No | NULL | | Array of strings |
| quick_links | JSON | No | NULL | | Array of `{label, url}` |
| created_at / updated_at | TIMESTAMP | Yes | now() | | |

**PK:** `id`. **FKs:** none. **Unique:** `slug`. **Relationships:** has many `departments`, has many `programmes`.

---

### Table: `departments`
**Purpose:** the Department layer, present for exactly 4 of 9 active schools today.
| Field | Type | Required | Default | Constraints | Description |
|---|---|---|---|---|---|
| id | BIGSERIAL | Yes | auto | PK | |
| school_id | BIGINT | Yes | — | FK → schools.id | |
| name | VARCHAR(200) | Yes | — | | |
| description | TEXT | No | NULL | | |
| image_path | VARCHAR(300) | No | NULL | | |
| display_order | INTEGER | No | NULL | | |
| careers | JSON | No | NULL | | |
| quick_links | JSON | No | NULL | | |
| created_at / updated_at | TIMESTAMP | Yes | now() | | |

**PK:** `id`. **FK:** `school_id → schools.id`. **Relationships:** belongs to `schools`; has many `programmes`.

---

### Table: `programme_categories`
**Purpose:** the real AI Bootcamp catalogue filter categories.
| Field | Type | Required | Default | Constraints | Description |
|---|---|---|---|---|---|
| id | BIGSERIAL | Yes | auto | PK | |
| slug | VARCHAR(80) | Yes | — | UNIQUE | e.g. `"cyber-security"` |
| label | VARCHAR(150) | Yes | — | | e.g. `"Cyber Security"` |
| icon | VARCHAR(80) | No | NULL | | Font Awesome class, as used today |

**PK:** `id`. **Relationships:** has many `programmes` (AI Bootcamp type only).

---

### Table: `programmes`
**Purpose:** every programme — academic (339 real entries) and AI Bootcamp (14 real entries) — in one table, per your instruction #1's preference to reuse rather than duplicate.
| Field | Type | Required | Default | Constraints | Description |
|---|---|---|---|---|---|
| id | BIGSERIAL | Yes | auto | PK | |
| programme_type | VARCHAR(20) | Yes | — | CHECK IN ('academic','ai_bootcamp') | |
| slug | VARCHAR(150) | Yes | — | UNIQUE | AI Bootcamp already has real slugs; academic programmes get one generated at migration |
| school_id | BIGINT | No | NULL | FK → schools.id | NULL for AI Bootcamp |
| department_id | BIGINT | No | NULL | FK → departments.id | Only set for the 4 schools that have departments |
| category_id | BIGINT | No | NULL | FK → programme_categories.id | AI Bootcamp only |
| name | VARCHAR(250) | Yes | — | | Academic `programme.name` / AI `course.title` |
| level | VARCHAR(50) | No | NULL | | Academic: Diploma/Certificate/Craft/Artisan. AI Bootcamp: `course.level` (e.g. "Intermediate") |
| level_class | VARCHAR(30) | No | NULL | | Academic only — drives the existing badge styling |
| duration | VARCHAR(50) | No | NULL | | e.g. `"2 Years"` / `"16 Weeks"` — flat duration; AI Bootcamp's *per-mode* duration overrides live on `programme_modes` |
| entry_requirement | TEXT | No | NULL | | Academic `entry` (e.g. "KCSE C- & above") / AI `whoFor` — same real-world concept, unified |
| exam_body | VARCHAR(50) | No | NULL | | Academic only (e.g. "KNEC") |
| overview | TEXT | No | NULL | | AI Bootcamp `overview`/`lead` |
| gain_points | JSON | No | NULL | | AI Bootcamp `gain[]` — array of strings, see §23 |
| image_path | VARCHAR(300) | No | NULL | | Academic `programme.image` / AI `heroImage` |
| apply_heading | VARCHAR(200) | No | NULL | | AI Bootcamp `applyHeading` |
| apply_subtext | VARCHAR(300) | No | NULL | | AI Bootcamp `applySubtext` |
| is_active | BOOLEAN | Yes | true | | |
| display_order | INTEGER | No | NULL | | |
| created_at / updated_at | TIMESTAMP | Yes | now() | | |

**PK:** `id`. **FKs:** `school_id → schools.id`, `department_id → departments.id`, `category_id → programme_categories.id` (all nullable). **Unique:** `slug`. **Relationships:** has many `programme_modes`, `programme_faqs`, `programme_features`; has many `applications`.

*Note: `careers`/`format`(duplicated) and `skills`/`projects`(dead) fields from `ai-courses-data.js` are deliberately **not** included — see Entity Decision Matrix §4.*

---

### Table: `programme_modes`
**Purpose:** the exact data behind the existing pricing cards (Full-Time Hybrid / Full-Time Remote / Part-Time Remote). Academic programmes have **zero** rows here (their price is the parent school's flat fee, §8).
| Field | Type | Required | Default | Constraints | Description |
|---|---|---|---|---|---|
| id | BIGSERIAL | Yes | auto | PK | |
| programme_id | BIGINT | Yes | — | FK → programmes.id | |
| mode_key | VARCHAR(30) | Yes | — | | `ft-hybrid` / `ft-remote` / `pt-remote`, matches current code exactly |
| label | VARCHAR(50) | Yes | — | | "Full-time" / "Part-time" |
| sub_label | VARCHAR(50) | No | NULL | | "Hybrid" / "Remote" |
| icon | VARCHAR(80) | No | NULL | | Font Awesome class |
| duration | VARCHAR(50) | No | NULL | | Per-mode duration override |
| start_date | DATE | No | NULL | | **NULL = "Contact Admissions" / "Applications Open"**, matching current renderer logic exactly (Step 0.5 §2) |
| fee_amount | DECIMAL(10,2) | No | NULL | | **NULL = "Contact Admissions"** (§8) |
| fee_currency | VARCHAR(10) | Yes | 'KES' | | |
| schedule | TEXT | No | NULL | | Free text, e.g. "Mon–Fri, 6PM–9PM E.A.T" |
| is_available | BOOLEAN | Yes | true | | Lets an admin hide a mode (e.g. cohort full) without deleting it |
| display_order | INTEGER | No | NULL | | |
| created_at / updated_at | TIMESTAMP | Yes | now() | | |

**PK:** `id`. **FK:** `programme_id → programmes.id`. **Relationships:** belongs to `programmes`; referenced (nullable) by `applications`.

---

### Table: `programme_faqs`
| Field | Type | Required | Default | Constraints | Description |
|---|---|---|---|---|---|
| id | BIGSERIAL | Yes | auto | PK | |
| programme_id | BIGINT | Yes | — | FK → programmes.id | |
| question | VARCHAR(300) | Yes | — | | |
| answer | TEXT | Yes | — | | |
| display_order | INTEGER | No | NULL | | |

**PK:** `id`. **FK:** `programme_id → programmes.id`.

---

### Table: `programme_features`
**Purpose:** the "What's Included" checklist items actually shown on the pricing cards (from `course.format`).
| Field | Type | Required | Default | Constraints | Description |
|---|---|---|---|---|---|
| id | BIGSERIAL | Yes | auto | PK | |
| programme_id | BIGINT | Yes | — | FK → programmes.id | |
| icon | VARCHAR(80) | No | NULL | | |
| title | VARCHAR(150) | Yes | — | | |
| description | TEXT | No | NULL | | |
| display_order | INTEGER | No | NULL | | |

**PK:** `id`. **FK:** `programme_id → programmes.id`.

---

### Table: `applicants`
| Field | Type | Required | Default | Constraints | Description |
|---|---|---|---|---|---|
| id | BIGSERIAL | Yes | auto | PK | |
| full_name | VARCHAR(200) | Yes | — | | |
| email | VARCHAR(200) | Yes | — | UNIQUE | |
| phone | VARCHAR(20) | Yes | — | | Stored with the "254" prefix, matching current payload |
| national_id | VARCHAR(30) | No | NULL | | Sensitive — §22 |
| date_of_birth | DATE | No | NULL | | Sensitive |
| gender | VARCHAR(20) | No | NULL | | |
| county | VARCHAR(50) | No | NULL | | |
| created_at / updated_at | TIMESTAMP | Yes | now() | | |

**PK:** `id`. **Unique:** `email`. **Relationships:** has many `applications`.

---

### Table: `applications`
| Field | Type | Required | Default | Constraints | Description |
|---|---|---|---|---|---|
| id | BIGSERIAL | Yes | auto | PK | |
| reference_code | VARCHAR(20) | Yes | — | UNIQUE | Public-safe identifier, §24 |
| applicant_id | BIGINT | Yes | — | FK → applicants.id | |
| programme_id | BIGINT | Yes | — | FK → programmes.id | |
| programme_mode_id | BIGINT | No | NULL | FK → programme_modes.id | Set only for AI Bootcamp applications |
| application_type | VARCHAR(30) | Yes | 'scholarship' | CHECK IN ('scholarship','general','programme_inquiry') | Absorbs both the full wizard and the lighter `aiApplyForm` — §9 |
| education_level | VARCHAR(50) | No | NULL | | |
| kcse_grade | VARCHAR(10) | No | NULL | | |
| consent | BOOLEAN | Yes | false | | |
| status | VARCHAR(20) | Yes | 'submitted' | CHECK, see §27 | |
| admin_notes | TEXT | No | NULL | | Internal only, never public |
| submitted_at | TIMESTAMP | Yes | now() | | |
| updated_at | TIMESTAMP | Yes | now() | | |

**PK:** `id`. **FKs:** `applicant_id → applicants.id`, `programme_id → programmes.id`, `programme_mode_id → programme_modes.id` (nullable). **Unique:** `reference_code`.

---

### Table: `alumni`
| Field | Type | Required | Default | Constraints | Description |
|---|---|---|---|---|---|
| id | BIGSERIAL | Yes | auto | PK | |
| full_name | VARCHAR(200) | Yes | — | | |
| email | VARCHAR(200) | Yes | — | UNIQUE | |
| phone | VARCHAR(20) | Yes | — | | |
| programme_id | BIGINT | No | NULL | FK → programmes.id | |
| graduation_year | INTEGER | No | NULL | CHECK (1990-2100 range) | |
| organisation | VARCHAR(200) | No | NULL | | |
| engagement_interests | JSON | No | NULL | | Array — Networking/Mentorship/Events/Career Opportunities |
| consent | BOOLEAN | Yes | false | | |
| registered_at | TIMESTAMP | Yes | now() | | |

**PK:** `id`. **FK:** `programme_id → programmes.id` (nullable). **Unique:** `email`.

---

### Table: `graduate_profile_requests`
| Field | Type | Required | Default | Constraints | Description |
|---|---|---|---|---|---|
| id | BIGSERIAL | Yes | auto | PK | |
| employer_name | VARCHAR(200) | Yes | — | | |
| company | VARCHAR(200) | No | NULL | | |
| email | VARCHAR(200) | Yes | — | | |
| phone | VARCHAR(20) | No | NULL | | |
| role_needed | VARCHAR(200) | No | NULL | | |
| message | TEXT | No | NULL | | |
| status | VARCHAR(20) | Yes | 'pending' | CHECK, see §27 | |
| submitted_at | TIMESTAMP | Yes | now() | | |

**PK:** `id`. **No FKs** — §12 explains why no `employers` table yet.

---

### Table: `partner_enquiries`
| Field | Type | Required | Default | Constraints | Description |
|---|---|---|---|---|---|
| id | BIGSERIAL | Yes | auto | PK | |
| organisation | VARCHAR(200) | Yes | — | | |
| contact_name | VARCHAR(200) | Yes | — | | |
| email | VARCHAR(200) | Yes | — | | |
| phone | VARCHAR(20) | No | NULL | | |
| enquiry_type | VARCHAR(30) | Yes | — | CHECK IN ('partnership','corporate_training') | §15 |
| message | TEXT | No | NULL | | |
| status | VARCHAR(20) | Yes | 'new' | CHECK, see §27 | |
| submitted_at | TIMESTAMP | Yes | now() | | |

**PK:** `id`. **No FKs.**

---

### Table: `contact_messages`
| Field | Type | Required | Default | Constraints | Description |
|---|---|---|---|---|---|
| id | BIGSERIAL | Yes | auto | PK | |
| name | VARCHAR(200) | Yes | — | | |
| email | VARCHAR(200) | Yes | — | | |
| subject | VARCHAR(200) | No | NULL | | |
| message | TEXT | Yes | — | | |
| status | VARCHAR(20) | Yes | 'new' | CHECK, see §27 | |
| submitted_at | TIMESTAMP | Yes | now() | | |

**PK:** `id`. **No FKs.**

---

### Table: `newsletter_subscribers`
| Field | Type | Required | Default | Constraints | Description |
|---|---|---|---|---|---|
| id | BIGSERIAL | Yes | auto | PK | |
| email | VARCHAR(200) | Yes | — | UNIQUE | |
| source_page | VARCHAR(100) | No | NULL | | Which of the 10 pages, §14 |
| consent | BOOLEAN | Yes | true | | |
| is_active | BOOLEAN | Yes | true | | |
| subscribed_at | TIMESTAMP | Yes | now() | | |
| unsubscribed_at | TIMESTAMP | No | NULL | | |

**PK:** `id`. **Unique:** `email`.

---

### Table: `admin_users`
| Field | Type | Required | Default | Constraints | Description |
|---|---|---|---|---|---|
| id | BIGSERIAL | Yes | auto | PK | |
| name | VARCHAR(200) | Yes | — | | |
| email | VARCHAR(200) | Yes | — | UNIQUE | |
| password_hash | VARCHAR(255) | Yes | — | | Never plaintext, §18 |
| is_active | BOOLEAN | Yes | true | | |
| last_login_at | TIMESTAMP | No | NULL | | |
| created_at / updated_at | TIMESTAMP | Yes | now() | | |

**PK:** `id`. **Unique:** `email`. **Security:** `password_hash` never included in any API response.

---

## 29. Complete ERD

```
schools
   │ 1:N
   ├──────────────< departments
   │                     │ 1:N
   │                     └──< programmes  ──┐
   │ 1:N (direct, when no department)       │
   └──────────────────────< programmes ─────┤
                                             │
programme_categories                        │
   │ 1:N                                    │
   └────────────────────────< programmes ───┤
                                             │
                                             ▼
                                        programmes
                                             │
                    ┌────────────┬───────────┼───────────┬─────────────┐
                    │ 1:N        │ 1:N       │ 1:N       │ 1:N         │
                    ▼            ▼           ▼           ▼             ▼
             programme_modes  programme_faqs programme_features   applications
                    │                                               ▲
                    │ 1:N (nullable)                                │ N:1
                    └───────────────────────────────────────────────┘

applicants
   │ 1:N
   └──< applications  (also FK → programmes, nullable FK → programme_modes)

alumni ──> programmes (nullable FK, "Programme Studied")

graduate_profile_requests   (standalone — no FK, §12)
partner_enquiries           (standalone — no FK, §15)
contact_messages            (standalone — no FK)
newsletter_subscribers      (standalone — no FK)
admin_users                 (standalone — no FK; referenced by future audit log, not built yet)
```

---

## 30. Frontend → Database Mapping

```
assets/js/ai-courses-data.js
    ↓
COURSES[] (14 objects)
    ↓ normalize
programmes (programme_type='ai_bootcamp')  ← slug, category, title, overview, whoFor, level, gain[], image
    ↓
programme_modes  ← modes[] (Full-Time Hybrid/Remote, Part-Time Remote — duration/startDate/fee/schedule)
programme_faqs   ← faqs[]
programme_features ← format[]
    ↓ (skills[], detailed projects[], careers[] deliberately NOT migrated — confirmed dead/duplicated data, §4)

assets/js/school-data.js
    ↓
SCHOOL_DATA{} (15 schools)
    ↓ normalize
schools  ← label, badge, icon, url, image, intro, count(derived), fee
    ↓
departments  ← departments[] (only hospitality/engineering/cosmetology/business)
    ↓
programmes (programme_type='academic')  ← programmes[] (name, level, levelClass, duration, entry, exam, image)
schools.careers / departments.careers  ← careers[] (JSON, not a table — §23)
schools.quick_links / departments.quick_links ← quickLinks[] (JSON, not a table — §23)

apply.html (the wizard's real fields)
    ↓
applicants  ← fullName, email, phone, nationalId, dateOfBirth, gender, county
applications ← mode/programme/school selections, educationLevel, kcseGrade, consent
    (programme_id / programme_mode_id resolved from the selections)
    ↓ (the existing fetch() to germaineinstitute.com is NOT the target of this mapping — §9/instruction #4)

alumni.html  →  alumni
graduate-hire.html (#gpForm)  →  graduate_profile_requests
partner-with-us.html + corporate-training.html (#cmForm)  →  partner_enquiries
contact.html  →  contact_messages
10× .newsletter-form  →  newsletter_subscribers
```

---

## 31. Database Seed Data Plan

Identified, **not inserted yet**:
- All 15 `schools` rows (from `school-data.js`)
- All `departments` rows for the 4 schools that have them (hospitality: 3, engineering: 3, cosmetology: 3, business: 2)
- All 339 real academic `programmes` rows
- All 14 AI Bootcamp `programmes` rows, their `programme_modes` (up to 3 each), `programme_faqs` (4-5 each), `programme_features` (3 each)
- The 9 real `programme_categories`
- One initial `admin_users` row (created manually/via a setup script when Phase 2 actually builds the dashboard — not seeded from any frontend data, since none exists)

---

## 32. Public vs Private Data

**Public API (no auth):** `schools`, `departments`, `programmes`, `programme_modes`, `programme_faqs`, `programme_features`, `programme_categories` — exactly what's already shown anonymously on the live site today.

**Authenticated/applicant-facing (Phase 3, if built):** an applicant checking their own `applications` status by `reference_code` — read-only, scoped to that one record, no listing.

**Admin-only:** `applicants`, `applications` (full), `alumni`, `graduate_profile_requests`, `partner_enquiries`, `contact_messages`, `newsletter_subscribers`, `admin_users`.

**Never exposed via any API, public or admin-list-view:** `admin_users.password_hash`; `applicants.national_id`/`date_of_birth` should be restricted even within the admin UI to only the specific application-review screen, not any general listing.

---

## 33. MVP / Phase 1 Tables

`schools`, `departments`, `programme_categories`, `programmes`, `programme_modes`, `programme_faqs`, `programme_features`, `applicants`, `applications`, `alumni`, `graduate_profile_requests`, `partner_enquiries`, `contact_messages`, `newsletter_subscribers` — **14 tables.** Everything the site needs to actually function (public catalogue + every real form persisting real data).

## 34. Phase 2 Tables

`admin_users` — **1 table.** The dashboard itself (queues, CRUD forms) is application code, not additional tables, once this exists.

## 35. Future Tables (Phase 3/4 — not built now)

- `application_documents` (Phase 3 — only once real file uploads are added to `apply.html`; not justified today, per instruction #5)
- `graduates` (Phase 3/4 — only once a real graduate-facing submission path exists)
- `employers` (Phase 3/4 — only once repeat-employer recognition is a real need, §12)
- `admin_activity_log` (Phase 3 — once multiple staff are actively editing records)
- A `role` column on `admin_users` (Phase 3/4 — additive, not a new table, §19)
- `news_articles` / `vacancies` — **explicitly not recommended**, per your instructions #6/#7; listed here only for completeness, not as a plan

---

## 36. PostgreSQL Recommendation

| | PostgreSQL | MySQL | SQLite |
|---|---|---|---|
| Relationships/constraints | Full FK, CHECK constraint support | Full FK support (InnoDB) | FK support exists but weaker enforcement by default |
| JSON columns (used here for `gain_points`, `careers`, `quick_links`) | Native `JSONB`, indexable, queryable | JSON type exists, less mature tooling | JSON supported via functions, weakest of the three |
| Production reliability | Excellent, mature | Excellent, mature | Not designed for concurrent production writes |
| Flask/SQLAlchemy support | First-class | First-class | First-class, but wrong tool for production here |
| Fit for this project's scale | Comfortably sufficient | Also sufficient | Fine for local dev/tests only |

**Recommendation: PostgreSQL** — specifically because this schema leans on a few genuine JSON columns (`gain_points`, `careers`, `quick_links` — §23's deliberate normalization calls), and PostgreSQL's `JSONB` is the most mature, indexable option of the three for that. MySQL would work almost as well and is a reasonable alternative if your hosting environment already standardizes on it. SQLite is recommended only as a local development/testing convenience, never for the deployed system.

---

## 37. Flask/SQLAlchemy Architecture Recommendation

Conceptual fit only — nothing installed or created:
- **SQLAlchemy** models mirror the table specs in §28 directly — one model class per table, relationships (`db.relationship`) matching the FKs described in §28/§29.
- **Alembic (via Flask-Migrate)** manages schema changes as the design evolves from Phase 1 → 2 → 3 — e.g., adding the `role` column to `admin_users` later is a one-line migration, not a rebuild.
- **Blueprints** align with the domains in §3: a `programmes` blueprint serving §32's public API, an `admissions` blueprint for `applicants`/`applications`, an `admin` blueprint gated behind auth for everything else.

**Reconciling the entity count against the earlier (pre-verification) plan:** that plan estimated 12 tables from a first-pass reading. This design has 14 (Phase 1) + 1 (Phase 2) = 15, because Step 0.5 found `school-data.js` was real structured data (adding `departments`, splitting programme content into `programme_modes`/`programme_faqs`/`programme_features` instead of flat columns) — more accurate, not more complicated for complexity's sake; every added table traces to something the Entity Decision Matrix (§4) confirms the frontend actually needs.

---

## 38. Final Table Count

**FINAL PROPOSED TABLE COUNT: 15** (14 Phase 1 + 1 Phase 2)

1. `schools` — real, structured source (`school-data.js`) drives 15 live pages
2. `departments` — real for 4 of 9 active schools
3. `programme_categories` — real AI Bootcamp filter values
4. `programmes` — unified academic + AI Bootcamp, both confirmed real
5. `programme_modes` — directly drives the existing, confirmed-dynamic pricing cards
6. `programme_faqs` — confirmed dynamically rendered
7. `programme_features` — confirmed dynamically rendered (pricing-card checklist)
8. `applicants` — real personal data from `apply.html`
9. `applications` — real multi-step form
10. `alumni` — real form
11. `graduate_profile_requests` — real form
12. `partner_enquiries` — real forms (2 pages, 1 shape)
13. `contact_messages` — real (if unwired) form
14. `newsletter_subscribers` — real (if unwired) forms, ×10
15. `admin_users` — minimum viable to operate any dashboard at all

**Not 12** (the earlier plan's estimate) because that plan predates the discovery of `school-data.js`'s real structure. **Not more than 15** because every candidate beyond this list (documents, graduates, employers, audit log, roles, news, vacancies) failed at least one of your instruction #11 questions ("does the current frontend require it?") and was deliberately deferred rather than built speculatively.

---

## 39. Risks / Open Questions — VALIDATION REQUIRED BEFORE SEEDING

These are explicitly **not** resolved by assumption anywhere in this document, and none of them are resolved by this correction pass either. Each must be confirmed by you before any seed/migration step runs against real data — no future migration or seed script may silently pick an answer for any of the six items below.

**A. School fee semantics** — `schools.fee` currently remains a **display string**, not a numeric per-programme fee, because the verified frontend contains exactly one school-level fee value per school (not per programme). Is that single flat fee a fixed price or a "starting from" figure? This determines whether `fee` should later be typed as decimal or stay a display string — kept as a string for now (§28) specifically so this isn't assumed. **Do not convert it to a numeric per-programme fee without verification.**

**B. Business school naming** — inconsistency between "School of Business & Commerce" (meta/title on `courses-business-commerce.html`) and "Business & Social Sciences" (that same page's own H1/body copy). **Not arbitrarily chosen** — needs your confirmation of the canonical name before `schools.name` is seeded.

**C. Six short-course pages** — `courses-short-course-*.html` were not found inside `school-data.js` during Step 0.5. **Do not assume they belong there** — their actual data source needs verification before they're migrated into `programmes`, or they may need their own separate migration path.

**D. AI Bootcamp application form (`application_type = 'programme_inquiry'`)** — the decision to unify the full scholarship wizard and the lighter `aiApplyForm` under one `applications` table via an `application_type` column (§9) is an **architectural judgment call**, not a verified frontend requirement. No frontend or database change has been made because of this — it remains a design note for your review, flagged explicitly rather than silently assumed.

**E. The unconfirmed external endpoint** (`germaineinstitute.com/application/clients/add`) — this design doesn't depend on it, per your instruction, but eventually someone needs to decide whether it's replaced, integrated, bridged temporarily, or retired.

**F. Alumni "Programme Studied" field is actually school-level** — re-verified directly against `alumni.html` (§11): the field labelled "Programme Studied" (`#aluProgramme`) offers only school names plus an AI Bootcamp catch-all as its options, not individual programmes. `alumni.programme_id → programmes.id` is left unchanged pending your decision on how to reconcile the FK with what the form actually collects — see §11's discrepancy note for the options considered (none of which have been chosen).

---

## 40. Final Database Readiness Checklist

- [x] Every required frontend form has a database destination
- [x] Every application has an applicant relationship
- [x] Every application has a programme relationship
- [x] Programmes belong to the correct academic structure (school → department where real → programme)
- [x] AI Bootcamp pricing can be represented (`programme_modes.fee_amount`)
- [x] AI Bootcamp learning modes can be represented (`programme_modes`, one row per mode)
- [x] AI Bootcamp intake information can be represented (`programme_modes.start_date`, NULL-aware)
- [x] Programme fees can change without editing HTML (admin edits `programme_modes.fee_amount` / `schools.fee`)
- [x] Alumni can be stored without unnecessary duplication (FK to `programmes`, not repeated text)
- [x] Graduate profile requests can be approved by admins (`status` workflow, §27)
- [x] Employer information is protected (admin-only, §32)
- [x] Partner enquiries can be stored
- [x] Contact enquiries can be stored
- [x] Newsletter subscribers can be stored
- [x] Admin users can be securely represented
- [x] Passwords are never stored in plaintext (hash only, §18)
- [x] Uploaded documents have secure metadata — deferred to Phase 3 by design, not overlooked (§5/§21)
- [x] Public APIs will not expose private data (§32)
- [x] Foreign-key relationships are defined (§28-29)
- [x] Important fields have appropriate indexes (§26)
- [x] Duplicate data is minimized (§23)
- [x] Static content is not unnecessarily placed in the database (News/Vacancies/gallery excluded, §16-17)
- [x] Existing AI Bootcamp data can be migrated (§30)
- [x] Existing academic programme data can eventually be migrated (§30)
- [x] The design is compatible with PostgreSQL (§36)
- [x] The design is compatible with Flask/SQLAlchemy (§37)

---

## Recommended Step 3

**Do not begin yet — per your Final Stop instruction, this is where I stop and wait for your review and approval of this database architecture.**

When you approve, Step 3 as you've scoped it would be: **Backend Project Architecture & Flask Setup** — project scaffolding, SQLAlchemy model files matching §28 exactly, Alembic initialization, and blueprint structure per §37 — still no live database, no running server, until you say so.
