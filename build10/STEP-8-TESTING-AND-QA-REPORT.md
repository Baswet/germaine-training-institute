# Germaine Training Institute — Step 8 Testing, Refinement & QA Report

**Date:** August 11, 2026. Scope: a full automated verification pass over the entire site and backend (public frontend, admin dashboard, CMS) using every tool genuinely available in this environment, with an honest account of what could and could not be checked without a real browser.

---

## A. Scope & Environment Constraints

This environment has no rendered-browser tooling (no Chrome/Playwright/Selenium available to this session). Every check below was therefore performed one of three ways:
1. **Automated backend tests** via Flask's test client (`pytest`) — exercises real HTTP requests, real session cookies, real CSRF validation, real database queries against an in-memory SQLite instance built from the exact same models used in production.
2. **Static analysis** — `node --check` for JavaScript syntax, Python's own tokenizer via `py_compile`, and custom scripts that parse every HTML file's actual markup (not a guess) to verify link targets, script/image sources, tag balance, duplicate IDs, and title/meta presence.
3. **Manual code review** — reading the actual route, service, template, and script source to verify security properties (CSRF coverage, auth enforcement, no hardcoded secrets, no raw SQL, safe file handling) rather than asserting them from memory.

What this pass **cannot** verify: actual rendered layout, responsive breakpoint behavior, animation/slideshow timing, real click-through user journeys, console errors that only appear at runtime in a browser, or visual regressions. Every finding below is scoped to what static analysis and a test client can honestly confirm. This limitation was flagged consistently throughout Steps 6 and 7 and applies identically here — it is not new to Step 8.

## B. Automated Test Suite Results

```
pytest (germaine-backend/): 149 passed, 0 failed, 0 warnings
python -m compileall/py_compile on every .py file: clean
```

Breakdown: 79 Step 5 baseline + 30 Step 7 admin-dashboard tests + 1 `level_class` test + 4 CORS tests + 1 net addition from the Step 7 CMS model-registry test restructuring (115 total pre-CMS) + 34 new Step 7 CMS tests (`tests/test_cms.py`) = **149**. Zero regressions at any point across this entire engagement's test count history (65 → 79 → 114 → 115 → 149).

## C. Full-Site Static Audit

Ran against all 59 real HTML pages in `build10/` (`hero-template.html` excluded — confirmed by grep to be an unlinked internal design-reference file, never reachable from the live site).

| Check | Result |
|---|---|
| Internal `href` link targets (3,354 checked) | 0 broken |
| `<script src>` targets | 0 broken |
| `<img src>` targets | 0 broken |
| `<title>` present | present on every real page (2 false-positive greps resolved — `course-detail.html`/`news-article.html` use `<title id="...">`, valid HTML) |
| `name="description"` meta present | present on every real page |
| JS syntax (`node --check`, 46 files) | all clean |
| CSS brace balance (all files in `assets/css/`) | all balanced |

## D. Navigation Consistency

Checked every page's `.nav-links` `<li>` count. Two distinct, intentional nav variants exist:
- **Standard 8-item nav** (Home / About / Admissions / Academic Schools / Languages & Short Courses / Student Life / News & Events / Contact) — used on the large majority of pages.
- **5-6 item "Employer & Industry Services" context nav** — used on `contact.html`, `partner-with-us.html`, `graduate-hire.html`, `corporate-training.html`. This is documented in-line in the markup itself ("Employer & Industry Services context menu — see graduate-hire.html for the same pattern") and traces back to an already-completed, already-approved task from earlier in this engagement (nav motto + employer-page context nav). Not a regression; confirmed intentional.

No unexplained nav variants found.

## E. Accessibility Findings & Fixes Applied

- **4 `<img>` tags on `index.html` had no `alt` attribute at all** (the "Practical Learning / TVET Approved / Career Focused / Student Success" feature icons). Fixed directly — added descriptive `alt` text to all 4. Zero visual impact (pure accessibility metadata), so this was corrected without asking, consistent with prior passes in this engagement that fix pure a11y/technical-correctness issues on sight.
- **Duplicate SVG `id="abWaveGrad"`** on `about.html` (two separate decorative wave-divider SVGs both defined a gradient with the same id — invalid per-document HTML, though both gradients were visually identical so there was no rendering difference). Fixed by renaming the second occurrence to `abWaveGrad2` and its local `url(#...)` reference. Verified no duplicate IDs remain anywhere on the page and the file's tag balance is unaffected.
- No other missing-alt or duplicate-ID issues found across the 6 CMS-touched pages (`index.html`, `about.html`, `campus.html`, `contact.html`, `news.html`, `news-article.html`) or in the broader sweep.

## F. HTML/CSS/JS Integrity

- Tag-balance check (div/section/article/header/footer/nav/main/ul/li/form) on every page touched during the CMS work: all balanced, both before and after the accessibility fixes in E.
- Every DOM element ID referenced by a CMS frontend bridge script (`homepage-cms-bridge.js`, `about-cms-bridge.js`, `student-life-cms-bridge.js`, `contact-info-cms-bridge.js`, `news-cms-bridge.js`, `news-article-detail.js`) was cross-checked against its target HTML file and confirmed to exist exactly once — no silently-broken selector.
- Full-repo `node --check` sweep (all 46 JS files, not just the 6 new ones): clean.

## G. CMS End-to-End Verification

Since no browser was available, "end-to-end" here means the full request/response cycle through Flask's real test client — login, real CSRF token fetched from a rendered form, real multipart file upload, real database writes and reads — not a mocked shortcut. Covered in `tests/test_cms.py` (34 tests) and re-confirmed in this pass:

- **News CMS test:** create a draft → edit it → publish (verifies the title+body requirement) → confirm it appears in the public `/api/news` list and is fetchable by slug with full body → unpublish → confirm it drops out of the public list → archive. Slug collision handling (`same-title` → `same-title-2`) verified.
- **CMS Image test:** valid PNG upload succeeds and is stored under a random `uuid4`-based filename (never the browser-supplied name); a `.php` payload disguised with a `.png` extension is rejected by the magic-byte content sniff; a `.txt` file is rejected by extension; alt-text update and archive both persist correctly; the admin media grid renders the public `url_path`, never a server filesystem path.
- **CMS acceptance test (empty-state safety):** confirmed at the API level that zero published articles → `/api/news` returns an empty list (200, not an error); an unset `SiteContent` key → `/api/site-content` returns `null` for that key; an empty `content_list_items` result → `/api/content-lists/<key>` returns `[]`. All three confirm the "empty CMS never blanks a public page" guarantee is real, not just documented.
- **Academics fee-separation guarantee:** confirmed a `fee` value posted to the programme-edit form is silently ignored (the underlying service function has no such parameter), while the same fee value posted to the school-edit form is correctly saved — proving the academic flat-fee and AI Bootcamp per-mode-fee pricing models cannot be cross-contaminated through the admin UI.

## H. Security Review

- **Secrets:** no hardcoded password/secret/API-key-shaped string literals found anywhere in `app/`. `.env` is git-ignored; only `.env.example` (placeholders) is tracked.
- **SQL injection surface:** none — every query in every service file goes through SQLAlchemy's ORM query builder; no raw SQL string concatenation or `db.text()` usage anywhere in the codebase.
- **CSRF:** every state-changing CMS route (content save, list-item create/update/archive, media upload/replace/alt-text/archive, news create/edit/publish/unpublish/archive, academics school/programme/mode/category update) validates the session-bound CSRF token; confirmed by both the automated test suite (`test_cms_post_without_csrf_token_is_rejected`, `test_media_upload_without_csrf_token_is_rejected`) and by reading every route function directly.
- **Authentication/authorization:** every CMS admin route is decorated with `admin_required` and confirmed (test + code read) to redirect unauthenticated requests to `/admin/login` without leaking any data first.
- **File upload safety:** extension allow-list + declared-MIME-type check + magic-byte content sniff, all three must agree; filenames are always a fresh `uuid4` token, never the browser-supplied name (no path traversal surface); files are stored under Flask's own static folder, never executed as code; `.php`/other executable-shaped uploads confirmed rejected by test.
- **CORS:** default is zero cross-origin headers (opt-in only via an empty-by-default env var), unchanged from the Step 7 decision and re-verified this pass.
- **XSS:** no rich-text/HTML field exists anywhere in the CMS — every admin-entered value is stored and rendered as plain text (Jinja's automatic autoescaping in admin templates, `.textContent` — never `innerHTML` on CMS data — in every public-facing frontend bridge script), so there is no script-injection surface for the CMS to introduce.
- **Public/admin separation:** confirmed the public `/api/...` surface never requires authentication and never exposes admin-only fields (password hashes, internal notes, etc.) — this was already covered by a Step 7 test and re-confirmed still passing.

## I. SEO Basic Check

Every real page carries a `<title>` and a `name="description"` meta tag (see C). No further SEO tooling (sitemap generation, structured data, Lighthouse-style scoring) was in scope for this pass and none was requested.

## J. Fix Priority Classification

| Priority | Item | Status |
|---|---|---|
| P2 | 4 missing `alt` attributes on `index.html` feature icons | **Fixed** this pass |
| P3 | Duplicate SVG gradient `id` on `about.html` (no visual effect, invalid HTML) | **Fixed** this pass |
| P3 | Homepage hero photo slideshow / Student Life Clubs & Sports lists not yet frontend-wired to the CMS (admin CRUD fully works; public display deferred — see Step 7 report Section K) | **Documented, not fixed** — requires browser-based verification of `hero-template.js`/`clubs-showcase.js`/`campus-gallery.js` slideshow-timing internals before it can be safely attempted |
| P3 | AI Bootcamp catalogue pages not wired to the live API (Step 7-era deferral, unchanged) | **Documented, not fixed** — same reasoning as Step 7 |
| — | No P0 (site-breaking) or P1 (major functional) issues were found anywhere in this pass | — |

No other issues were found. This is a genuinely small list because the engagement has been verified incrementally at every prior step rather than accumulating problems for a single end-of-project pass.

## K. Regression Confirmation

Final full-suite run after every fix in this report: **149 passed, 0 failed.** No test was skipped, weakened, or removed to make this pass.

## L. Not Covered in This Pass (Honest Gaps)

- Rendered visual/responsive verification across breakpoints (mobile/tablet/desktop) — no browser available.
- Real user click-through journeys (visitor applying for a scholarship, admin publishing a news article end-to-end in a live UI) — approximated via the test client's HTTP-level equivalent, not a literal browser session.
- Browser console/network error inspection — no browser available to generate or read console output.
- Cross-browser compatibility (Safari/Firefox/Edge quirks).
- Performance/Lighthouse-style auditing.
- Production deployment configuration, hosting, domains, or credentials — explicitly out of scope per your instructions, not attempted.

These gaps are identical in kind to the ones already disclosed in the Step 7 report and are not new limitations introduced by this pass — they are a consequence of the sandbox environment, stated plainly rather than implied away.

## M. Step 8 Status

```
STEP 8 COMPLETE
```

Every check genuinely available in this environment was run: the full automated test suite (149/149), a full-site static link/script/image audit (0 broken references across 59 pages), a navigation-consistency check (2 intentional variants, both explained), an accessibility pass (2 real issues found and fixed), an HTML/CSS/JS integrity sweep (all clean), an end-to-end CMS verification via the test client (News/Media/Academics/empty-state guarantees all confirmed working, not just asserted), and a manual security code review (no secrets, no SQL injection surface, CSRF/auth fully enforced, safe file handling, correct public/admin separation). No P0 or P1 issues were found. The two P3 items carried forward are pre-existing, already-documented scope deferrals from Step 7, not new problems.

No deployment, hosting purchase, domain configuration, or production credential setup was performed or attempted, per your explicit Step 8 stop condition. Step 9 has not been started.
