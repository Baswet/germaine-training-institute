derer# Germaine Training Institute — Frontend Cleanup Report

**Date:** August 11, 2026
**Project:** `build10/`
**Backup:** a full zip of the project was made before any change (`build10-backup-final.zip`, 278 MB, delivered alongside this report). No design was changed — only file organisation, broken references, and dead code were addressed.

---

## Scope decision: keeping the existing flat structure

Your brief offered a `pages/`, `css/base|components|pages`, `js/core|components|pages` structure as an example but explicitly said to deviate if the project would benefit from something else. This project already has 58 HTML pages at the root plus `assets/css/` (35 files), `assets/js/` (40 files), and `assets/images/` (285 files, well-organised into `hero/`, `schools/`, `gallery/`, `partners/`, `facilities/`, `industries/`, etc.) — a convention that's been consistently applied and cross-referenced across roughly 140 prior development tasks on this site.

**I did not do a full physical move into nested `pages/`/`css/`/`js/` folders.** Rewriting ~58 pages' worth of relative paths (every `href`, `src`, `<link>`, `<script>`) for a purely organisational relabeling — with zero functional benefit, since the current structure is already consistent and every reference already resolves correctly — is a large-blast-radius change for a live, working site. If you'd still like the deeper nested restructure, I'd recommend doing it as its own dedicated, carefully staged pass rather than folded into this cleanup — say the word and I'll scope it properly. Everything below is the cleanup that was safe to do without that risk.

---

## A. Files Organized

**Discovered but not part of the Germaine site** — flagged, not touched:
- `EarnCash/` — a separate, fully-built referral/commission platform (own Flask backend, own MySQL schema, own frontend) living inside `build10/`, wired into every page's nav as "Earn Cash Fast." Per your decision, this is documented only and excluded from the Germaine backend plan (see `BACKEND-AUDIT-AND-PLAN.md`).
- `AUDIT_REPORT.md` — a pre-existing audit from July 22, 2026 covering an earlier Germaine+EarnCash integration pass. Left in place at the project root; still useful history.

**Archived (moved, not deleted)** into `_archive/2026-08-11-cleanup/`, after confirming zero references anywhere in the live project via full-project grep:
| File | Why |
|---|---|
| `assets/css/admissions-premium.css` | Not linked from any page — `admissions.html` uses `premium-theme.css` + `scholarship.css` instead |
| `assets/css/graduate-qualities.css` | Orphaned; the "Graduate Qualities" section that used it was removed from `graduate-hire.html` in a prior redesign pass |
| `assets/js/graduate-qualities.js` | Same as above |
| `assets/js/school-extras-data.js` | Zero references anywhere |
| `assets/js/student-life-hero.js` | Orphaned after `campus.html`'s hero was rebuilt to clone the Alumni hero design in a prior pass; its `<script>` tag was already removed at that time |
| `assets/images/partners/nita-approved.jpg` + `nita-approved (1).jpg` | Superseded duplicates — every page uses `nita.png` instead |
| `assets/images/hero/download (2).jpg` | Unreferenced anywhere, unclear/default filename |

**Left alone, not junk despite appearances:**
- `hero-template.html` + its `hero-template.css`/`.js`/background video/poster — not linked from nav, but self-consistent and not broken. Likely an intentional design reference (this matches a finding in the pre-existing `AUDIT_REPORT.md` too). Flagged for your call in "Needs Decision" below.
- `course-detail.html` + `assets/js/course-detail.js` + `assets/js/courses-data.js` — an older, self-contained course-detail template that predates the `ai-course-*` system. Nothing links to it, but it's internally complete and not broken. Flagged below.
- ~62 `.fuse_hidden********` files at the project root and one `.write_test` file — these are filesystem-level temporary artifacts from the mounted drive (created when a file is rewritten while something else has it open), not real project files. One was tested for safe removal and behaved as expected (a zero-content ghost entry that simply vanished). I've left the rest alone rather than risk unpredictable behavior moving 62 of them blindly — they're invisible to the live site (nothing references them) and harmless. Worth a one-time manual delete from your end if you want them gone, or they'll likely keep clearing on their own as the mount cycles.

---

## B. Images Organized

- **285 images/videos, 213.6 MB total.** Folder organisation (`hero/`, `schools/`, `gallery/`, `gallery-2026/`, `partners/`, `facilities/`, `industries/`, `about/`, `campus/`, `students/`, `slide/`) was already sensible and left as-is.
- **99 images (67.8 MB) are not referenced by any current HTML/CSS/JS** — verified by checking every image's filename against the text of every page, stylesheet, and script (including `ai-courses-data.js`'s dynamic image fields, and `corporate-bento.js`'s gallery array, both of which use fully-spelled literal filenames, not programmatic path construction — so this check is reliable, not a guess).
  - **The bulk of this (~20 files) is `assets/images/gallery-2026/`** — a folder of real, camera-named photos (`img_1579.jpg`, `img_1408.jpg`, etc.) that is not referenced by a single page anywhere. This looks like prepared-but-never-wired-in content, not junk — **flagged in "Needs Decision" below rather than archived**, since moving real, substantial photo content without asking felt like the wrong call.
  - The rest is scattered across `slide/`, `schools/`, and `gallery/` — largely large stock/Pexels photography that was likely sourced for a section that ended up using different final images. Full file-by-file list available on request; I didn't move these since, unlike the 7 files in section A, there isn't a confirmed "superseded by X" story for each one — just "currently unused."
- **Unclear filenames found:** `download (2).jpg` (archived — genuinely unused) and `nita-approved (1).jpg`/`nita-approved.jpg` (archived — both superseded by `nita.png`). No other meaningfully-unclear filenames turned up; the project's naming (`school-engineering.jpg`-style, Pexels-attributed, or purpose-named like `hero-corridor.jpg`) is already largely descriptive.
- **Broken images: zero.** Every `<img src>` across all 58 pages resolves to a real file.
- **object-fit / cropping:** not modified — no evidence of incorrect cropping was found in this pass; this would need visual (browser) verification, which is outside what a text-based audit can confirm. Flagged under Remaining Issues.

---

## C. Broken Links Fixed

**Full link audit result: 0 broken `href`s, 0 broken image paths, 0 broken CSS `<link>`s, 0 broken `<script>` paths across all 58 pages.** This site's internal linking is in excellent shape.

Two real fixes were made — both were placeholder (`href="#"`) hero CTAs on `index.html` with an obvious, unambiguous correct destination:

| Element | Page | Was | Fixed To | Status |
|---|---|---|---|---|
| "Apply Scholarship Now" hero button | `index.html` | `href="#"` | `apply.html` (the real scholarship application wizard) | **Fixed** |
| "Explore Programmes" hero button | `index.html` | `href="#"` | `courses.html` (the real programme catalogue) | **Fixed** |

**Working (already correct, verified, left alone):** all utility-bar links (Hire our Graduates → `graduate-hire.html`, AI Bootcamps → `ai-bootcamp.html`, Corporate Training, Partner with Us, Alumni Registration → `alumni.html`, Vacancies), all 14 AI Bootcamp programme cards (fixed in a prior pass this project — verified still correct), all 26 academic school page cross-links, all footer nav.

**Needs Decision — placeholder links with no obvious destination (not invented, not touched):**
- 5 footer social icons (Facebook, Instagram, LinkedIn, YouTube, TikTok) on every single page → `href="#"`. These need your real social media URLs; there's no "obvious existing page" to connect them to.
- 2 `data-cm-trigger` buttons on `corporate-training.html` (`href="#"`) — these are **not actually broken**; they're intentionally intercepted by `consultation-modal.js` to open a modal instead of navigating. Working as designed.

**Needs Backend:** every real form's submit action (see Form Audit below) and the Vacancies page, which currently has no "Apply for this role" action at all.

---

## D. Buttons Without Destinations

| Button/Link | Page(s) | Classification |
|---|---|---|
| Facebook / Instagram / LinkedIn / YouTube / TikTok icons | All 58 pages (footer) | **NEEDS DECISION** — awaiting real social URLs |
| Newsletter "Subscribe" | 10 pages (About, Admissions, Apply, course-detail, 4× courses-*, News) | **BACKEND REQUIRED** — no JS handler exists at all, plain form submit currently does nothing |
| `data-cm-trigger` consultation buttons | `corporate-training.html` (×2) | **INTENTIONALLY NON-FUNCTIONAL as a link** — JS-driven modal trigger, working as designed |
| All 6 real form submit buttons (Apply, Alumni Register, AI Bootcamp Apply, Consultation, Request Graduate Profile, Partner With Us) | Respective pages | **BACKEND REQUIRED** — see Form Audit |
| Contact Us submit | `contact.html` | **BACKEND REQUIRED** — and currently has zero JS wired at all (not even a fake-success state) |
| Vacancies "view/apply" actions | `vacancies.html` | **BACKEND REQUIRED** — no application flow exists yet in the frontend |

No dead buttons were left unexplained — every non-working button above falls into one of the classifications your brief specified.

---

## E. Forms Requiring Backend

All 7 real forms + the 10 newsletter boxes. **Zero forms currently persist data anywhere.** Full detail (fields, current JS behavior, exact file/line) is in `BACKEND-AUDIT-AND-PLAN.md` §1.2 — summarised here:

1. Scholarship Application Wizard (`apply.html`) — the one form with a real (if unconfirmed) live `fetch()` POST already wired to `https://www.germaineinstitute.com/application/clients/add`
2. AI Bootcamp Apply (`ai-bootcamp.html`)
3. Alumni Register (`alumni.html`)
4. Contact Us (`contact.html`) — **no JS at all**, not even a fake success state
5. Corporate Training Consultation (`corporate-training.html`)
6. Request Graduate Profile (`graduate-hire.html`)
7. Partner With Us (`partner-with-us.html`)
8. Newsletter signup (10 pages) — **no JS at all**

None were connected to any real or fake backend during this cleanup, per your explicit instruction.

---

## F. Broken Images Fixed

None found — 0 broken image paths across the entire project (see §C). Nothing to fix here.

---

## G. CSS Issues Fixed

- 35 CSS files audited for brace balance and duplicate/orphaned status.
- 1 fully orphaned file found and archived (`admissions-premium.css` — see §A).
- No unbalanced braces, no `!important`-heavy sections beyond what's already load-bearing for the deliberate glassmorphism/travelling-light layering pattern used consistently across the site (that pattern is a designed feature, not a defect).
- No conflicting media queries found between files that share a page.
- The existing brand system (pink/blue/white, glassmorphism, travelling lights, cards, responsive rules) was not touched.

---

## H. JavaScript Issues Fixed

- 40 JS files audited. 3 fully orphaned files found and archived (`graduate-qualities.js`, `school-extras-data.js`, `student-life-hero.js` — see §A).
- One inconsistency flagged rather than silently fixed: `assets/css/schools-dashboard.css` is actively loaded by `courses.html`, but its logical JS counterpart, `assets/js/schools-dashboard.js`, is loaded nowhere — meaning either an interactive "schools dashboard" feature was planned and never wired up, or the JS was intentionally dropped and the CSS is now dead weight. I didn't guess which — flagged in Remaining Issues.
- No duplicate `<script>` tags found on any page.
- No fake/simulated network calls were altered — per your instruction, forms that currently show a fake success state were left exactly as they are; that's frontend behavior that will get replaced when the backend lands, not a bug to patch now.

---

## I. Pages Checked

All 58 real Germaine pages: `index.html`, `about.html`, `admissions.html`, `apply.html`, `contact.html`, `news.html`, `courses.html` + all 26 `courses-*.html` school/short-course pages, `ai-bootcamp.html`, `ai-bootcamp-courses.html` + all 14 `ai-course-*.html` detail pages, `campus.html`, `alumni.html`, `graduate-hire.html`, `partner-with-us.html`, `corporate-training.html`, `vacancies.html`. Plus the two orphaned-but-intact legacy pages, `hero-template.html` and `course-detail.html`.

---

## J. Remaining Issues (need your decision or can't be safely automated)

1. **`assets/images/gallery-2026/`** — ~20 real, unwired photos. Keep, wire into a page, or archive? Not touched.
2. **`hero-template.html`** and **`course-detail.html`** (+ their dedicated CSS/JS) — both orphaned from nav but internally intact. Keep as reference, or archive?
3. **`schools-dashboard.js` is missing** while `schools-dashboard.css` is active on `courses.html` — possible incomplete feature. Worth a quick look at what the CSS classes expect before deciding whether to write the missing JS or strip the CSS.
4. **Footer social media links** — need real URLs from you (Facebook/Instagram/LinkedIn/YouTube/TikTok).
5. **Newsletter signup is inconsistent** — only present on 10 of 58 pages, with no backend behind it on any of them. Worth deciding whether it should be sitewide once wired up, or intentionally limited.
6. **1 duplicate `id`** found: `abWaveGrad` appears twice in `about.html` (a decorative SVG element, not a functional one — low risk, but flagging as requested).
7. **Minor accessibility gaps:** `course-detail.html` has no `<title>`; `hero-template.html` has no meta description; `about.html` and `graduate-hire.html` have no `<h1>` (both likely because their hero headline is a styled `<span>`/`<div>` rather than a literal `<h1>` tag — worth a quick pass since it affects both SEO and screen-reader page identification); 5 `<img>` tags site-wide are missing `alt` text (4 are decorative icons on `index.html`, 1 more on `about.html`).
8. **Visual/responsive verification** (horizontal overflow, clipped travelling-light borders, cards breaking at specific breakpoints) could not be done in this pass — this audit was text/code-based, with no live browser available to render and screenshot every breakpoint. I'd recommend a manual click-through or a follow-up pass with browser tooling before you fully sign off on "no visual regressions."
9. **62 leftover `.fuse_hidden*` files + 1 `.write_test` file** at the project root — harmless mount-level artifacts, not project files, left alone rather than risk unpredictable removal behavior (see §A).

---

## K. Backend Preparation — what's now ready

- Every form's exact field set, current (fake) JS behavior, and file location is documented in `BACKEND-AUDIT-AND-PLAN.md`.
- Every CTA that needs a real destination once the backend exists is identified — nothing is a mystery dead button.
- The one already-real integration point (`apply.html`'s `fetch()` to `https://www.germaineinstitute.com/application/clients/add`) is flagged prominently so you can confirm whether that endpoint should be the real target or gets replaced.
- The programme/school data model is fully mapped: `ai-courses-data.js` is the one existing structured data source (ready to seed a `programmes` table directly); the 26 academic school pages' content is hardcoded HTML with no data file, so it'll need manual entry into the database in Phase 1 of the backend plan.
- Zero broken paths, zero orphaned code left silently in place — everything either got archived with a documented reason or got flagged for your explicit decision.
