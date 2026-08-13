# Germaine Backend — API Documentation (Step 5)

All responses use one JSON envelope:

```json
// success
{"success": true,  "data": <any>, "message": "..."}
// error
{"success": false, "data": null,  "message": "...", "errors": {"field": ["..."]}}
```

`errors` is only present for `422` validation failures. No response body ever includes a stack trace, database credential, or password hash.

None of these endpoints are called by any existing frontend page yet — that wiring is a deliberately separate, future step.

---

## Public blueprint (`/api/...`, no auth)

### `GET /api/health`
Liveness check. No database access. → `200 {"status": "ok", "service": "germaine-backend", "time": "..."}` (not wrapped in the envelope — unchanged since Step 3).

### `GET /api/schools`
List schools. **Query params:** `active_only` (`true`/`false`, default `true`). → `200`, `data` = array of school objects (`id, slug, name, description, image_path, fee, is_active, careers, quick_links, programme_count`).

### `GET /api/schools/<slug>`
School detail, including its departments. → `200` on found; `404` if no school matches `slug`.

### `GET /api/schools/<slug>/departments`
Departments for one school. → `200`, `data` = array; `404` if the school doesn't exist.

### `GET /api/programme-categories`
The 9 real AI Bootcamp categories. → `200`, `data` = array of `{slug, label, icon}`.

### `GET /api/programmes`
*(Step 7: each item now also includes `level_class` — the existing, already-seeded badge-styling column from Step 2 §28, previously stored but not serialized. No schema/migration/seed change.)*

Search/filter the unified programme catalogue. **Query params (all optional):**
- `school` — school slug
- `department_id` — integer
- `category` — category slug (AI Bootcamp only)
- `type` — `academic` | `ai_bootcamp`
- `q` — keyword, matched against programme name
- `active_only` — default `true`
- `page` (default 1), `per_page` (default 20, max 100)

→ `200`, `data = {items: [...], total, page, per_page}`. `422` if `type` is invalid or pagination params are out of range. `404` if `school`/`category` slug doesn't exist.

Each item's `pricing` field reflects the real, distinct pricing models (Step 2 §8): academic programmes report `{"type": "flat_school_fee", "fee": "<school.fee string>"}`; AI Bootcamp programmes report `{"type": "per_mode_fee", "modes": [...]}` with each mode's `fee_amount`/`start_date` as `null` (`"Contact Admissions"` in the paired `*_display` field) exactly when the underlying column is `NULL`.

### `GET /api/programmes/<slug>`
Full programme detail — adds `overview`, `gain_points`, `faqs`, `features`, and (for AI Bootcamp) full per-mode pricing. → `200`; `404` if not found.

---

## Admissions blueprint (`/api/admissions/...`, no auth)

### `POST /api/admissions/applications`
Create an application. **Body:**

| field | required | notes |
|---|---|---|
| `full_name` | yes | ≤200 chars |
| `email` | yes | valid email, ≤200 chars — matches/creates the `Applicant` by this email (Step 2 §9) |
| `phone` | yes | ≤20 chars |
| `programme_id` | yes | must reference an active `Programme` |
| `consent` | recommended | boolean |
| `programme_mode_id` | conditional | forbidden for academic programmes; if given for an AI Bootcamp programme, must belong to that programme |
| `application_type` | no | `scholarship` (default) / `general` / `programme_inquiry` |
| `national_id`, `date_of_birth` (`YYYY-MM-DD`), `gender`, `county`, `education_level`, `kcse_grade` | no | |

→ `201`, `data` = application summary including the new `reference_code`. `422` on any validation failure (missing fields, bad email, invalid `application_type`, mode/programme mismatch). `404` if `programme_id` doesn't exist or is inactive.

### `GET /api/admissions/applications/<reference_code>`
Read-only status lookup, scoped to exactly one record (Step 2 §32 — never a listing). → `200`; `404` if the code doesn't exist.

### `GET /api/admissions/scholarship-info`
Static description of the scholarship workflow (no invented eligibility/financial rules — Step 2 §10). → `200`.

---

## Alumni blueprint (`/api/alumni/...`, no auth)

### `POST /api/alumni/register`
**Body:** `full_name`, `email`, `phone` required; `programme_id`, `graduation_year` (1990-2100), `organisation`, `engagement_interests` (array), `consent` optional. → `201`; `422` on validation failure or a duplicate email.

---

## Enquiries blueprint (`/api/enquiries/...`, no auth)

### `POST /api/enquiries/graduate-requests`
**Body:** `employer_name`, `email` required; `company`, `phone`, `role_needed`, `message` optional. → `201`.

### `POST /api/enquiries/partner-enquiries`
**Body:** `organisation`, `contact_name`, `email`, `enquiry_type` (`partnership`|`corporate_training`) required; `phone`, `message` optional. → `201`; `422` if `enquiry_type` is invalid.

### `POST /api/enquiries/contact-messages`
**Body:** `name`, `email`, `message` required; `subject` optional. → `201`.

### `POST /api/enquiries/newsletter-subscriptions`
**Body:** `email` required; `source_page`, `consent` optional. Idempotent — resubmitting the same email returns the existing subscriber (and reactivates it if previously unsubscribed) rather than erroring or duplicating. → `201`.

---

## Admin blueprint (`/api/admin/...`)

**Unchanged since Step 3 — still a placeholder, no routes.** No authentication system was built in Step 5 (deliberately out of scope — Step 2 §19 defers roles/permissions, and no login/session mechanism has been approved yet).

---

## Errors

Every error uses the same envelope. Status codes in use: `400`, `401` (handler registered, unused — no auth exists yet), `403` (handler registered, unused), `404`, `409` (handler registered, unused — no endpoint currently raises a conflict), `422`, `500`. `422` responses always include `errors: {field: [messages]}`.
