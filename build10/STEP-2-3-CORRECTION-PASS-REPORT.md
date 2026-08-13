# Germaine Training Institute — Step 2 / Step 3 Correction Pass Report

**Date:** August 11, 2026. **Documentation and static-verification corrections only.** No database was created, no migration was generated or applied, no data was seeded, no API was built, and the frontend was not connected to the backend.

---

## A. Documentation Corrections

**Step 2 Executive Summary (§1).** "The result is 14 tables for Phase 1+2 (MVP + Admin)" — read as if 14 were the grand total — corrected to: "The result is **15 tables across Phase 1 and Phase 2: 14 Phase 1 tables plus 1 Phase 2 admin table**."

**Step 2 §39 "Risks / Open Questions — VALIDATION REQUIRED BEFORE SEEDING".** Confirmed items A-E were already present and unresolved in the authoritative document (fee semantics, Business school naming, six short-course pages, `programme_inquiry` judgment call, the external endpoint). Added a clarifying preamble sentence stating that no future migration or seed step may silently resolve any of them. A sixth item, **F**, was added — see the alumni finding below.

**Step 3 final report's description of §39.** Previously said §39 contained "four lettered items" and listed only A-D, silently dropping E (the external endpoint) from the *summary*, even though E was always present in the actual Step 2 document. Corrected to state five items, A-E, with E's endpoint explicitly spelled out, plus a note that F was newly added during this pass.

**Applicant matching wording (Step 2 §9).** Previously said applicants are "looked up/created by email+phone," which read as a composite matching key the table spec never defined. Corrected to state applicants are matched primarily by their **unique email address** (`applicants.email` is `UNIQUE`); phone is retained as an additional identifying/contact field, not a second matching key. **The database model was not changed.**

**Alumni programme relationship (Step 2 §11) — genuine discrepancy found.** Re-read `alumni.html` directly: the field is labelled "Programme Studied" (`<label for="aluProgramme">Programme Studied *</label>`) and named `programme` (`<select id="aluProgramme" name="programme">`), but its actual `<option>` values are **9 school names** ("School of Medical & Health Sciences," "School of Engineering," "Business & Social Sciences," etc.) plus one catch-all "Germaine AI Bootcamp" option — no individual programmes are listed at all. So the real field is a school-level selector wearing a programme-level label. This was not caught in the original Step 2 pass. **No model change was made** — `alumni.programme_id → programmes.id` is untouched. The discrepancy is now documented in §11 and flagged as new item **F** in §39, exactly as instructed: found, documented, flagged, not guessed at or silently fixed.

**Step 3 report wording about which sections were edited.** "Was edited (not rewritten) in two places" corrected to name every section actually touched by all correction work to date: **§1, §5, §9, §11, and §39**; no other section of the Step 2 document was changed.

**Entity-count consistency sweep.** Searched both documents for every "14 tables" / "15 tables" / "Phase 1" / "Phase 2" / "Final total" / "Final Table Count" / "MVP / Phase 1 Tables" / "Phase 2 Tables" occurrence. All now consistently reconcile to **15 total = 14 Phase 1 + 1 Phase 2**; no remaining statement implies 14 or any other number is the grand total.

---

## B. Navigation Status

**Unchanged and not redesigned**, confirmed by re-running static checks rather than by assumption:
- `initStickyHeader()` remains the single authoritative scroll/hysteresis mechanism, thresholds unchanged (`ACTIVATE_AT=80` / `DEACTIVATE_AT=60`).
- `initNavbarTransparency()` remains removed from the init sequence in `main.js` (`node --check` passes).
- `header-premium.js` unchanged (`node --check` passes).
- The `graduate-hire-elevate.css` page-specific nav re-theme remains removed; brace balance re-verified (124 open / 124 close).
No hero, card, footer, background, image, typography, or content changes were made anywhere.

---

## C. Backend Status

- **15 models confirmed** in `germaine-backend/app/models/`: 14 Phase 1 + 1 Phase 2 (`AdminUser`), matching Step 2 §28 exactly.
- **No speculative models** — `test_no_forbidden_speculative_models_defined` passes.
- Flask scaffold unchanged except for the verification runs below (no source files under `germaine-backend/` were modified in this pass).
- **All 18 tests pass**: `18 passed in 4.16s`.

---

## D. Database Status

**No database was created, no migration was generated or applied, and no seed data was inserted.** `migrations/versions/` remains empty. No `db.create_all()` call exists anywhere. No connection to any PostgreSQL server (live or otherwise) was attempted during this pass.

---

## E. Frontend Status

**No frontend form was rewired and the existing external application endpoint remains untouched.** Nothing under `build10/` was modified in this pass beyond what was already reported as complete in the prior navigation-correction work (§B above) — `apply-wizard.js`'s `fetch()` call to `germaineinstitute.com/application/clients/add` was not read or touched.

---

## F. Remaining Validation Items

1. **School fee semantics** — is `schools.fee` a fixed price or a "starting from" figure?
2. **Business school canonical name** — "School of Business & Commerce" vs. "Business & Social Sciences."
3. **Six short-course pages** — their real data source is still unverified; do not assume `school-data.js`.
4. **AI Bootcamp `programme_inquiry` decision** — unifying the lighter AI inquiry form into `applications` remains an architectural judgment call, not a confirmed frontend requirement.
5. **Existing external application endpoint** (`germaineinstitute.com/application/clients/add`) — still undecided whether it will be replaced, integrated, bridged, or retired.
6. **(Newly identified this pass) Alumni "Programme Studied" field is actually school-level** — `alumni.programme_id` points at `programmes`, but the real form only ever collects a school (or "AI Bootcamp"), never an individual programme. Needs your decision on how to reconcile the FK before any alumni seed/migration.

Static verification performed and passing: `python -m compileall germaine-backend` (clean), `pytest` (18/18), `node --check` on `main.js` and `header-premium.js` (both clean), CSS brace balance on `graduate-hire-elevate.css` (124/124). No `flask db migrate` or `flask db upgrade` was run; no live database was created or connected to.

---

**STOP — No migration, database creation, seeding, API implementation, authentication implementation, or frontend integration is authorized by this correction pass.**
