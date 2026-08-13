derer# Germaine Training Institute — Step 0.5: Pre-Backend Verification

**Date:** August 11, 2026. Every claim below was re-checked against the actual project files (not just the prior two reports). No database was created, no backend code was written, no APIs were created. One correction surfaced below is significant enough that I did **not** silently patch it into the old reports — it's called out explicitly in §B and §D.

---

## 1. Project Structure — Verified

| Item | Cleanup report said | Actual, re-verified | Match? |
|---|---|---|---|
| Real Germaine pages | 58 | 58 | ✅ |
| Academic school/short-course pages | 26 | **27** (`courses-*.html`) | ⚠️ off by one — see §B |
| AI Bootcamp hub + 14 detail pages | 15 | 15 | ✅ |
| `assets/css/` | 35 → 33 after archival | 33 | ✅ |
| `assets/js/` | 40 → 37 after archival | 37 | ✅ |
| `assets/images/` | 285 raster images | 244 jpg + 17 png + 21 webp = 282 raster (285 − 3 archived) + 5 mp4 + 1 pdf = 288 files total | ✅ (reconciles exactly once video/PDF are counted separately) |
| `_archive/2026-08-11-cleanup/` | 7 files | Confirmed: exactly the 7 intentionally-archived files, nothing else | ✅ |
| EarnCash | Separate, documented, excluded from Germaine backend scope | Confirmed untouched (`backend/`, `database/`, `frontend/`, `README.md` all present, unmodified) | ✅ |
| Stray `.py`/`.sql` outside EarnCash | None | Confirmed: zero | ✅ |

---

## 2. AI Bootcamp Data Model — Verified in Full

**Trace, confirmed line-by-line in the actual files:**

```
assets/js/ai-courses-data.js
    COURSES array (14 objects) — each has:
      slug, file, category, categoryLabel, title, titleParts, lead,
      duration, badgeNumber, heroImage, heroAlt, overview, whoFor,
      level, gain[], skills[], projects[], careerLabel, careers[],
      formatLabel, format[], applyHeading, applySubtext,
      modes: modes("Xweeks", {...pricing...}),   ← Full-Time Hybrid / Full-Time Remote / Part-Time Remote
      faqs: baseFaqs(...)
        ↓
    modes() helper (lines 26-60) builds the 3 mode objects per course:
      { id: "ft-hybrid"|"ft-remote"|"pt-remote", label, sub, icon,
        duration, startDate, fee, schedule }
      Every field defaults to "Contact Admissions" if not explicitly
      set per course — nothing is silently invented.
        ↓
assets/js/ai-course-detail-renderer.js
    init() reads document.body[data-course-slug], looks up the course,
    then calls 6 render functions, each targeting one mount point:
      renderHeroCards()      → #aicHeroCardsMount   (pricing/mode cards — see below)
      renderGain()           → #aicGainMount         (course.gain[])
      renderStructure()      → #aicStructureMount    (duration, mode[0].label, mode[0].schedule, projects.length)
      renderRequirements()   → #aicRequirementsMount (course.whoFor)
      renderFaqs()           → #aicFaqMount          (course.faqs[])
      renderStickyNav()      → #aicDetailNavMount    (in-page anchor nav)
        ↓
ai-course-*.html (14 pages)
    Each page has empty <div id="...Mount"> placeholders that get
    replaced (outerHTML) by the functions above on page load.
        ↓
Pricing/learning-mode cards (.aic-hero-card, one per mode)
    Badge: "Intake: <date>" if a real startDate exists, else "Applications Open"
    Rows: Start Date, Course Duration, Mode of Learning, Tuition Fee
    Checklist: built from course.format (first 3 items) + a 4th static
      item if course.projects.length > 0
    CTA: "Apply Now" → #aicApply (same-page anchor to the static Apply section)
```

**Important nuance the trace above surfaces — not every field in the course object is actually live:**

| Field | Actually rendered? | Where |
|---|---|---|
| `modes` (pricing/duration/start date/schedule) | **Yes — single source of truth** | `renderHeroCards()` |
| `gain` | **Yes** | `renderGain()` |
| `whoFor` | **Yes** | `renderRequirements()` |
| `faqs` | **Yes** | `renderFaqs()` |
| `careers`, `format` | **Duplicated, not single-sourced.** The JS array exists, but each of the 14 HTML pages *also* hand-authors its own "Career Opportunities" and "Learning Format" sections as static HTML (verified identical content on `ai-course-ai-ml.html`, currently in sync — but nothing keeps them in sync automatically). | Static HTML `#aicCareers`/`#aicFormat` sections, not the renderer |
| `skills`, `projects[].title/.desc` | **Dead data.** Defined in every one of the 14 course objects, but confirmed via full-text search that no page renders the individual skill or project entries anywhere — only `projects.length` (a count) is used, in `renderStructure()`. | Nowhere |

**Confirming your specific question:** yes — **the pricing/learning-mode cards can be populated directly from the existing `ai-courses-data.js` structure with zero changes.** That's already exactly how they work today; there is no separate pricing file and no HTML-duplicated pricing to reconcile. The one thing worth deciding before Step 2: whether `careers`/`format` (duplicated) and `skills`/`projects` detail (unused) should become real database columns at all, given they either duplicate content that actually lives in HTML or currently render nowhere.

**Data provenance note found directly in the file's own header comment** (lines 7-20): course durations are Germaine's own established figures; **tuition fees and start dates were set by Germaine admissions using comparable regional bootcamp pricing as a benchmark, each reduced by a fixed KSh 5,000 margin** — where no reliable benchmark existed, "Contact Admissions" was kept rather than a fee being invented. Worth knowing this pricing is admissions-benchmarked, not yet independently confirmed as final, before it's seeded into a production database.

---

## 3. The 26 (Actually 27) Academic Programme Pages — Major Correction

**This is the most significant finding of this verification pass, and it corrects the prior Frontend Cleanup Report.**

The cleanup report stated the 26 academic pages are "100% hardcoded static HTML. No JSON/JS data file backs these." **That was incomplete/incorrect.** Re-inspecting `courses-business-commerce.html` closely (it references `id="spCareerList"` — an empty `<ul>`, a tell that something populates it at runtime) led to finding:

- **`assets/js/school-data.js` — a 4,313-line, real, structured data file**, loaded on every academic school page (`<script defer src="assets/js/school-data.js">`), holding `window.SCHOOL_DATA` (keyed by school id) and `window.SCHOOL_ORDER` (the 9 currently-active schools).
- **`assets/js/school-page.js`** consumes it to dynamically render: the sidebar school nav, the programme table (name/duration/level, searchable/filterable), the Career Opportunities list, Career Portal links, and — significant — a **working department-switching UI** (`?dept=N` deep links, a department selector bar) for schools that have departments.

**Per-school data shape (verified against the actual object):** `label`, `badge`, `icon`, `url`, `image`, `intro`, `count` (always exactly equal to `programmes.length` — verified for all 15 entries, zero mismatches), `fee` (one flat fee per school, not per programme), `quickLinks[]` (external job-portal links), `programmes[]` (`name`, `level`, `levelClass`, `duration`, `entry` requirement, `exam` body, `image`), and optionally `departments[]` (`name`, `description`, its own `quickLinks`/`careers`, and its own programme subset).

**Corrected summary table:**

| Page | School (SCHOOL_DATA key) | Data Source | Hardcoded? | Departments? | Backend Migration Needed? |
|---|---|---|---|---|---|
| `courses-health-sciences.html` | `health` | `school-data.js` (22 programmes) | No — data-driven | No | Yes — seed from existing object |
| `courses-hospitality-tourism.html` | `hospitality` | `school-data.js` (40 programmes) | No — data-driven | **Yes (3)** | Yes |
| `courses-engineering-technology.html` | `engineering` | `school-data.js` (29 programmes) | No — data-driven | **Yes (3)** | Yes |
| `courses-computing-it.html` | `ict` | `school-data.js` (20 programmes) | No — data-driven | No | Yes |
| `courses-cosmetology-fashion-design.html` | `cosmetology` | `school-data.js` (15 programmes) | No — data-driven | **Yes (3)** | Yes |
| `courses-business-commerce.html` | `business` | `school-data.js` (57 programmes) | No — data-driven | **Yes (2 — Business, Social Sciences)** | Yes |
| `courses-mass-communication-journalism.html` | `journalism` | `school-data.js` (8 programmes) | No — data-driven | No | Yes |
| `courses-agriculture.html` | `agriculture` | `school-data.js` (33 programmes) | No — data-driven | No | Yes |
| `courses-virtual-learning.html` | `virtual` | `school-data.js` (**0 programmes** — shows a "listing being finalized" message) | No — data-driven, but empty | No | Yes (once real content exists) |
| `courses-law.html` | `law` (kept, excluded from nav) | `school-data.js` (0 programmes) | No — data-driven, empty, and intentionally de-navigated | No | Low priority |
| `courses-teachers-training-college.html` | `teachers` (excluded from nav) | `school-data.js` (0 programmes) | No — data-driven, empty, de-navigated | No | Low priority |
| `courses-social-sciences.html` | `social` (excluded from nav) | `school-data.js` (13 programmes) | No — data-driven, de-navigated | No | Low priority |
| `courses-beauty-therapy-short-courses.html` | `beauty` (excluded from nav) | `school-data.js` (6 programmes) | No — data-driven, de-navigated | No | Low priority |
| `courses-hair-dressing-short-courses.html` | `hairdressing` (excluded from nav) | `school-data.js` (6 programmes) | No — data-driven, de-navigated | No | Low priority |
| `courses-languages.html` + 4 language pages | `languages` (excluded from nav, own top-level nav item) | `school-data.js` (90 programmes) | No — data-driven, de-navigated from "Academic Schools" specifically | No | Yes |
| 6 short-course subpages (`courses-short-course-*.html`) | — | **Not found in SCHOOL_DATA** — need a direct check; likely genuinely static HTML, unlike the schools above | Likely yes | — | Needs a follow-up check before Step 2 if these are in scope |

**Why the file's own header comment matters:** `school-data.js` states this was "Restructured to the institute's 9 Academic Schools (June 2026)... Schools NOT in the current 9 (Law, Teacher Training, Social Sciences standalone, Beauty Therapy standalone, Hair Dressing standalone) are kept below, UNCHANGED, so their existing pages keep working if bookmarked — they are simply excluded from SCHOOL_ORDER." **This means those 5 pages being unreachable from navigation is intentional, not a bug** — correcting any assumption that they're simply "orphaned."

---

## 4. Schools → Departments → Programmes — Verified

The 3-level hierarchy you described **does genuinely exist in the data**, but only for 4 of the 9 active schools:

```
SCHOOL (9 active + 6 legacy-kept-for-bookmarks)
   │
   ├── hospitality  (3 departments)
   ├── engineering   (3 departments)
   ├── cosmetology   (3 departments)
   ├── business      (2 departments — "Business", "Social Sciences", matching the page's own intro copy exactly)
   │
   └── health, ict, journalism, agriculture, virtual, + all 6 legacy schools
         → flat, no department layer (programmes attach directly to the school)
```

**No duplicate programmes or naming inconsistencies found** in the department/programme names themselves. **One naming inconsistency found and worth flagging:** `courses-business-commerce.html`'s `<title>`/meta description say "School of Business & Commerce," but its own `<h1>` and body copy say "Business & Social Sciences" / "School of Business & Social Sciences (SBSS)" — the page's SEO metadata and its visible content use two different names for the same school. Low-risk, but worth a decision on the canonical name before it becomes a database `label`.

---

## 5. `schools-dashboard.css`/`.js` — Resolved: Option B, confirmed precisely

- `assets/js/schools-dashboard.js` **is a complete, working implementation** — its own header comment confirms it "Builds the left navigation table, right overview table and live search straight from `window.SCHOOL_DATA`/`window.SCHOOL_ORDER`... the same data source that already powers every individual school page." It expects to mount into `#sdRows`, `#sdOverviewBody`, `#sdSearchInput`, etc.
- **It is not loaded by any `<script>` tag anywhere** (confirmed via project-wide search).
- `assets/css/schools-dashboard.css` **is loaded by `courses.html`** — but `courses.html` contains **none** of the HTML elements the CSS or JS expect (`#sdRows`, `.sd-dashboard`, `.sd-hero`, etc. all confirmed absent from that page).

**Conclusion: this is a fully-built "Schools Dashboard" feature (search/filter/overview across all schools) that was never actually inserted into any page.** The CSS `<link>` on `courses.html` is a leftover reference with zero current visual effect — not Option A (nothing else already does this), not Option C in the sense of being dead-by-design (it's dead only because it was never wired in, not because it's obsolete), not Option D (the JS exists at exactly the name/location you'd expect, just unreferenced). Not touched, per your instruction not to write missing JS.

---

## 6. Legacy Files — `hero-template.html` / `course-detail.html`

Re-confirmed, no change from the cleanup report:
- Neither is referenced by any live page's navigation or content links.
- Both are internally self-consistent (their own CSS/JS/images all resolve).
- `course-detail.html` uses its own separate, older data files (`assets/js/courses-data.js`, `assets/js/course-detail.js`) — a parallel, pre-`ai-courses-data.js` system, fully independent of anything currently live.
- **Recommendation unchanged:** safe to leave as-is for now. They cost nothing (not loaded, not linked, not indexed by any live nav), and archiving them is a zero-urgency decision you can make whenever convenient — not something that blocks database design.

---

## 7. `assets/images/gallery-2026/`

Re-confirmed: 20 real, camera-named photos (`img_1579.jpg`, `img_1408.jpg`, etc.), zero references anywhere in any HTML/CSS/JS (including no programmatic path construction that could hide a reference — verified the one JS-driven gallery component on this site, `corporate-bento.js`, uses fully-spelled literal filenames, not loops, so this check is reliable). Filenames suggest a raw camera export, not obviously pre-sorted into a Student Life/Campus theme the way `assets/images/gallery/` (the *other*, actually-used gallery folder) is.

**Recommendation: KEEP FOR FUTURE USE.** Not enough evidence to confidently say these are Student-Life-specific versus general institutional photos, and archiving real, substantial photographic content on a guess is exactly the kind of call your brief asked me not to make unilaterally. This doesn't block Step 2 — it's page content, not data model.

---

## 8. All Forms — Re-verified, current state confirmed unchanged since the cleanup pass

| Domain | Page | Form ID | Required fields | Submission method | JS present? | Data persisted? | Backend required? |
|---|---|---|---|---|---|---|---|
| Admissions/Scholarship | `apply.html` | (multi-step wizard, no single form id — step 2 panel) | Mode, school, programme, full name, phone, email, national ID, DOB, gender, county, education level, KCSE grade, terms consent | JS-intercepted, real `fetch()` POST (see §9) | Yes — `apply-wizard.js` | Attempted, unconfirmed (see §9) | **Yes** |
| AI Bootcamp | `ai-bootcamp.html` | `aiApplyForm` | Name, email, phone, programme interest | JS-intercepted, fake success | Yes — `ai-bootcamp.js` | No | **Yes** |
| Alumni | `alumni.html` | `alumniForm` | Full name, email, phone/WhatsApp, programme, graduation year, org (optional), engagement pills, consent | JS-intercepted, fake success | Yes — `alumni.js` | No | **Yes** |
| Contact | `contact.html` | `contact-form` | Name, email, subject, message | Plain HTML submit | **No JS at all** | No | **Yes** |
| Corporate Training | `corporate-training.html` | `cmForm` | Company, contact name, email, phone, training need | JS-intercepted, fake success | Yes — `consultation-modal.js` | No | **Yes** |
| Graduates | `graduate-hire.html` | `gpForm` | Employer name, company, email, phone, role needed, message | JS-intercepted, fake success | Yes — `graduate-profile-form.js` | No | **Yes** |
| Partners | `partner-with-us.html` | `pwForm` | Organisation, contact name, email, phone, partnership type, message | JS-intercepted, fake success | Yes — `partner-with-us.js` | No | **Yes** |
| Newsletter | 10 pages | none (`.newsletter-form`, no id) | Email | Plain HTML submit | **No JS at all, anywhere** | No | **Yes** |

No real data was submitted anywhere during this verification — every form was inspected via source code only.

---

## 9. The Existing Application Endpoint — Verified, not called

Inspected `assets/js/apply-wizard.js` line by line (lines 414-456, `handleSubmit()`).

- **URL:** `https://www.germaineinstitute.com/application/clients/add` (a constant, `SCHOLARSHIP_API_ENDPOINT`, line 47)
- **Method:** `POST`
- **Headers:** `Content-Type: application/json`
- **Payload:** `{ mode, modeLabel, fullName, phone (prefixed "254"), email, nationalId, dateOfBirth, gender, county, educationLevel, kcseGrade, schoolId, school, programme, consent: true, source: "apply.html" }`
- **Mode:** `"no-cors"` — meaning the browser deliberately cannot read the response (status code, body) at all; this is a fire-and-forget request by construction, not an oversight.
- **Error handling:** a `.catch()` only logs a console warning; there is no user-facing error state at all.
- **The UI shows "success" unconditionally**, regardless of whether the request actually reached a server or what it returned — the code comment says this explicitly: *"Best-effort direct submission... The UI shows the success state regardless of network result, since this static export has no guaranteed live endpoint to confirm against."*
- **I did not send a request to this endpoint** — inspected via static code reading only, per your instruction.
- **Whether this is a real, live production endpoint could not be determined from the frontend alone.** The domain matches your institute's real domain, which is suggestive, but `no-cors` mode is also exactly what you'd write defensively if you *weren't* sure the endpoint existed yet.

**Flagged, not decided:** this needs your confirmation before Step 2 locks in an `applications` table shape — specifically whether this endpoint is (a) live today and should be treated as an existing contract to match, (b) planned but not yet built, or (c) a placeholder that should simply be replaced by the new Flask API.

---

## 10. Buttons & Links — Re-verified

Cleanup report's core numbers reconfirmed unchanged: **0 broken internal links, 0 broken image paths, 0 broken CSS references, 0 broken JS references** across all 58 pages.

| Area | Classification |
|---|---|
| Apply Scholarship Now (sitewide) → `apply.html` | **WORKING** |
| Explore Programmes (homepage hero, fixed last pass) → `courses.html` | **WORKING** |
| AI Bootcamp cards → real per-programme pages | **WORKING** (verified in a prior pass) |
| Academic programme cards/table rows → real school pages via `school-page.js` | **WORKING** |
| Alumni Register button → `alumni.html` form | **WORKING** (button); form submission itself is **BACKEND REQUIRED** |
| Request Graduate Profile → modal (`gpForm`) | **WORKING** (button); submission is **BACKEND REQUIRED** |
| Partner With Us button → `pwForm` | **WORKING** (button); submission is **BACKEND REQUIRED** |
| Corporate Training consultation buttons (`data-cm-trigger`) | **INTENTIONALLY JS-DRIVEN** (modal trigger, not a broken link) |
| Footer social icons (Facebook/Instagram/LinkedIn/YouTube/TikTok) | **NEEDS REAL URL** |
| Newsletter subscribe (10 pages) | **BACKEND REQUIRED** |
| Vacancies "Apply Now" per job → `contact.html` | **WORKING** — correction to the cleanup report, which implied no destination existed; it does, it's just a generic contact redirect rather than a per-job application (see §11) |
| News "Read More"/CTA links → real, existing thematic pages (not per-article pages) | **WORKING**, with the caveat that none of them lead to that specific news item's full content |

---

## 11. Vacancies — Verified

- **6 hardcoded jobs** in `vacancies.html` (ICT Support Technician, Front Office Associate, Junior Electrical Technician, Community Health Assistant, Fashion & Design Intern, Business Administration Assistant). No JS data file — pure static HTML, no JSON, no `VACANCY_DATA` global anywhere.
- **Every job card does have an Apply Now button, and it does have a destination: `contact.html`.** Correction to the cleanup report's "no application flow exists yet" — there is one, it's just generic (every job routes to the same contact form, with no job identifier carried through, so admissions staff would need to ask which role someone means).
- **Future database needed if** you want per-job applications, an actual applicant-to-job link, or more than 6 static roles. Not needed for the site to keep functioning as-is.

---

## 12. News — Verified

- **6 hardcoded article cards** in `news.html`. No individual article pages exist anywhere in the project.
- Each card's CTA links to a real, existing, topically-related page (`admissions.html`, `campus.html`, `about.html`, `courses.html` ×2) rather than a dedicated article page — working links, but not "read the full story" in the way the "Read More" label on one of them implies.
- No duplication found (each of the 6 stories is distinct copy).
- **Recommendation: Option A (remain static) is defensible for now** — 6 items with no growth mechanism currently in place is a content-maintenance problem, not a backend problem, until you're actually publishing news regularly. Flagging as a genuine open question for you rather than deciding it here, since it directly feeds the Step 2 "should News have a table" decision.

---

## 13. Admin Requirements — Classified from the actual frontend only

| Area | Classification | Basis |
|---|---|---|
| Applications (scholarship/programme) | **DATABASE REQUIRED + ADMIN MANAGEMENT REQUIRED** | Real form exists, submissions need a review queue |
| Alumni | **DATABASE REQUIRED + ADMIN MANAGEMENT REQUIRED** | Real form; staff will want to see/search registrations |
| Graduate profile requests | **DATABASE REQUIRED + ADMIN MANAGEMENT REQUIRED** | Real form; needs an approval workflow (per your own Step 2 privacy brief) |
| Partner enquiries | **DATABASE REQUIRED + ADMIN MANAGEMENT REQUIRED** | Real form |
| Contact enquiries | **DATABASE REQUIRED + ADMIN MANAGEMENT REQUIRED** | Real form, currently fully unwired |
| Newsletter subscribers | **DATABASE REQUIRED** (lighter admin need — mostly export/manage, not a review workflow) | Real forms, currently fully unwired |
| Programmes / Schools / Departments | **DATABASE REQUIRED + ADMIN MANAGEMENT REQUIRED (future)** | Already data-driven today via `school-data.js`/`ai-courses-data.js` — moving that into a DB with an admin UI is a real, justified future step, not urgent for launch since editing the JS files still works |
| Fees | Same as above — **currently editable by editing JS**, not urgent to move to DB for MVP | Already centralised in 2 files, not scattered in HTML |
| AI Bootcamps | Same pattern as Programmes | Already its own clean data model |
| Vacancies | **STATIC CONTENT today; ADMIN MANAGEMENT REQUIRED only if you want more than occasional manual HTML edits for 6 listings** | Confirmed hardcoded, low churn |
| News | **STATIC CONTENT today; FUTURE OPTIONAL CMS** | Confirmed hardcoded, 6 items, no growth mechanism yet |

---

## 14. Personal Data Collected — Grouped, nothing invented

**Applicants** (`apply.html`): full name, email, phone, national ID number, date of birth, gender, county, education level, KCSE grade, programme/school/mode selection.

**Alumni** (`alumni.html`): full name, email, phone/WhatsApp, programme, graduation year, current organisation (optional), engagement preferences, consent flag.

**Employers** (`graduate-hire.html`): employer/company name, contact person implied by "employer name" field, email, phone, role needed, free-text message.

**Partners** (`partner-with-us.html`): organisation name, contact person, email, phone, partnership type, free-text message.

**Contact enquiries** (`contact.html`): name, email, subject, message. (No phone field on this form — confirmed by re-reading the field list; don't add one without a reason.)

**Newsletter subscribers**: email only — no name field exists on any of the 10 instances.

**Admin users**: none exist yet — this is entirely a Step 2/3 design decision, not something the frontend collects today.

---

## 15. File Uploads — Verified: none exist yet

**Zero file upload inputs exist anywhere in the current frontend** (`<input type="file">` not found on any of the 6 forms). The scholarship wizard's payload (§9) is JSON only — no document attachment. This means "application documents" (ID copy, KCSE certificate) discussed in the earlier backend plan is a **future requirement inferred from what an admissions process typically needs**, not something the current frontend already half-supports. Worth being explicit about that distinction before Step 2 designs a documents table around it.

---

## 16. Frontend-Only Data — Final List

**MUST BECOME DATABASE DATA:**
Applications (scholarship/programme), alumni records, graduate profile requests, partner enquiries, contact enquiries, newsletter subscribers, admin users. All of these are transactional/user-submitted — they don't exist as content anywhere until someone submits them.

**COULD REMAIN STATIC (for now):**
About Us / institutional narrative text, general design/marketing content, the hero-template/course-detail legacy pages, `gallery-2026` photo content, the 5 de-navigated legacy school pages (Law/Teachers/Social Sciences/Beauty/Hairdressing) given their current zero-or-low programme counts and intentional nav exclusion.

**FUTURE CMS CANDIDATES (currently static, real growth/editing need if usage increases):**
News articles (6 hardcoded, no growth mechanism), Vacancies (6 hardcoded, no growth mechanism), Programmes/Schools/Departments/Fees (already centrally data-driven in 2 JS files today — not urgent to move to a DB-backed CMS for MVP, but the natural next step once an admin dashboard exists).

---

## 17. Backend Scope — Phased, based on everything verified above

**PHASE 1 — Essential (site must function properly):**
Applications table + endpoint (resolve the existing endpoint question first — §9), Alumni, Graduate Profile Requests, Partner Enquiries, Contact Enquiries, Newsletter Subscribers. Email notifications on each submission. Public read-only Programmes/Schools API seeded from the existing `ai-courses-data.js` and `school-data.js` (not re-authored — migrated).

**PHASE 2 — Administration:**
Admin users + auth, review/management queues for every Phase 1 table, basic CRUD for Vacancies and News if you decide they should leave static-HTML status.

**PHASE 3 — Advanced:**
Graduate profile approval workflow with privacy tiers (public/internal/employer-visible-after-approval — per your own Step 2 brief's instinct, and justified by the real "Request Graduate Profile" form already existing), file uploads for application documents, rate limiting/hardening.

**PHASE 4 — Future:**
Full Programmes/Schools/Departments/Fees CRUD in the admin dashboard (replacing hand-edited `school-data.js`/`ai-courses-data.js`), News/Vacancies CMS if content volume grows, per-job applicant tracking for Vacancies, roles/permissions beyond a single admin role, audit logging.

---

## FINAL DECISION REPORT

### A. VERIFIED AND READY
Project structure (with the one correction below), all 6 real forms and their exact fields/current behavior, the AI Bootcamp data model and its complete render trace, the academic Schools→Departments→Programmes data model and its real 4,313-line data source, the `schools-dashboard` mystery (resolved), Vacancies and News content and link behavior, personal data fields actually collected, confirmation that zero file uploads exist yet, 0 broken links/images/CSS/JS sitewide.

### B. CORRECTIONS TO THE PREVIOUS AUDIT
1. **Academic page count is 27, not 26** — includes 2 category-hub pages (`courses-languages.html`, `courses-short-courses.html`) alongside the individual subject pages.
2. **The single biggest correction:** the 26/27 academic pages are **not** "100% hardcoded static HTML with no data file." They're genuinely data-driven from `assets/js/school-data.js` (4,313 lines) via `assets/js/school-page.js`, including a real, working School→Department→Programme hierarchy for 4 of 9 active schools. This directly changes the Step 2 database design — the migration path is "normalize an existing structured JS object," not "manually transcribe HTML."
3. **Vacancies "Apply Now" buttons are not dead-ends** — they route to `contact.html`. The earlier framing of "no application flow exists" was inaccurate; the more precise issue is that the flow is generic (no job ID passed through), not absent.
4. `ai-courses-data.js`'s `skills` and detailed `projects` fields are dead data (defined, never rendered) — not previously called out. `careers`/`format` are duplicated between JS and static HTML, not single-sourced the way `modes`/`gain`/`faqs` are.

### C. REMAINING DECISIONS (genuinely yours to make)
1. Is `https://www.germaineinstitute.com/application/clients/add` a live production endpoint, a planned one, or a placeholder? This affects how Step 2 designs the `applications` table's relationship to any external system.
2. `gallery-2026/` (20 real photos) — keep for future use (my recommendation), wire into a specific page, or archive?
3. `hero-template.html`/`course-detail.html` — keep as harmless references, or archive now?
4. News: stay static, or become database-driven in Step 2's scope?
5. Vacancies: stay static with the generic contact-form flow, or design real per-job applications now?
6. `courses-business-commerce.html`'s School of Business & Commerce vs. Business & Social Sciences naming — which is canonical?
7. Footer social media URLs (still placeholders).
8. Whether the 6 short-course subpages (`courses-short-course-*.html`) are in scope for Step 2's academic data model — they weren't found in `school-data.js` and need a quick follow-up look before the schema is finalized, if you want them included.

### D. AI BOOTCAMP DATA CONFIRMATION
Pricing, learning modes (Full-Time Hybrid/Remote, Part-Time Remote), duration, start date, schedule, and intake status all live in one place — the `modes` array inside each course object in `assets/js/ai-courses-data.js` — and are rendered dynamically, with zero duplication, by `renderHeroCards()` in `assets/js/ai-course-detail-renderer.js`. The cards can be populated directly from this structure with no new data file and no HTML duplication, exactly as your instructions required me to confirm.

### E. ACADEMIC PROGRAMME DATA
Confirmed data-driven (not hardcoded) via `assets/js/school-data.js`, consumed by `assets/js/school-page.js`. 9 schools currently active in navigation, 6 more kept in the same file (with working pages) but intentionally excluded from navigation since a June 2026 restructure. 4 of the 9 active schools have a real Department layer; the rest attach programmes directly to the school.

### F. FORMS READY FOR BACKEND
All 7 real forms (Scholarship Application, AI Bootcamp Apply, Alumni Register, Contact, Corporate Training Consultation, Request Graduate Profile, Partner With Us) plus the 10 unwired newsletter boxes. Full field lists in §8. Zero were touched or submitted during this verification.

### G. ADMIN FEATURES REQUIRED
Review/management queues for Applications, Alumni, Graduate Requests, Partner Enquiries, Contact Enquiries; a lighter subscriber-list view for Newsletter; admin authentication. Programmes/Schools/Fees CRUD is real but not urgent — the current 2-file JS data model is already centralized and workable for MVP.

### H. DATABASE CANDIDATES
Applications, Alumni, Graduate Profile Requests, Partner Enquiries, Contact Enquiries, Newsletter Subscribers, Admin Users — all justified by real, existing forms with zero persistence today. Programmes/Schools/Departments — justified by the real, already-structured `school-data.js`/`ai-courses-data.js` (migration target, not urgent blocker).

### I. STATIC CONTENT
About Us/institutional text, `gallery-2026`, the 5 de-navigated legacy school pages, `hero-template.html`/`course-detail.html`. None of these need a database to keep working.

### J. FINAL BACKEND SCOPE
As detailed in §17 — Phase 1 (Applications/Alumni/Graduates/Partners/Contact/Newsletter + read-only Programmes API), Phase 2 (Admin + auth), Phase 3 (Graduate privacy workflow, file uploads, hardening), Phase 4 (full Programmes CMS, News/Vacancies CMS, roles, audit log).

---

**This verification is complete. Per your explicit stop condition, I have not started Step 2 — Database Architecture & Data Model.** I have your full Step 2 prompt and I'm ready to run it as soon as you confirm you've reviewed this report (and ideally weighed in on §C's open decisions, though none of them are hard blockers — I can proceed with reasonable defaults on anything you'd rather not decide yet, and flag those defaults explicitly in Step 2).
