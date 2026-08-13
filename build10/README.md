derer# Germaine Training Institute — Website

Static multi-page HTML/CSS/JS site (no build tooling, no framework). This README documents the project as of August 11, 2026, after a full frontend cleanup/audit pass — see `FRONTEND-CLEANUP-REPORT.md` and `BACKEND-AUDIT-AND-PLAN.md` for the detailed findings behind this summary.

## Project Structure

The project intentionally keeps its existing flat structure rather than nesting into `pages/`/`css/`/`js/` subfolders (see the cleanup report's "Scope decision" for why):

```
build10/
├── index.html, about.html, contact.html, ...      # 58 real pages at the root
├── courses-*.html                                  # 26 academic school/short-course pages
├── ai-course-*.html                                 # 14 AI Bootcamp programme detail pages (data-driven)
├── assets/
│   ├── css/            # 35 stylesheets, one shared (style.css, responsive.css, ...) + per-section files
│   ├── js/              # 40 scripts, same pattern
│   └── images/          # hero/, schools/, gallery/, gallery-2026/, partners/, facilities/, industries/, ...
├── _archive/2026-08-11-cleanup/   # confirmed-unused files moved here during cleanup (not deleted)
├── EarnCash/             # separate, independently-built referral platform — own backend/frontend, documented but out of scope for the Germaine backend plan
├── AUDIT_REPORT.md        # prior audit (July 22, 2026)
├── BACKEND-AUDIT-AND-PLAN.md
└── FRONTEND-CLEANUP-REPORT.md
```

## Main Pages

Home, About, Admissions, Apply (Scholarship Wizard), Programmes (`courses.html` + 26 school pages), AI Bootcamp (hub + 14 programme pages), Student Life (`campus.html`), Alumni, Hire Our Graduates, Partner With Us, Corporate Training, Vacancies, Contact, News.

## Assets

Images live under `assets/images/`, already organised by section (hero, schools, gallery, partners, facilities, industries, about, campus, students). Shared CSS/JS conventions: `assets/css/style.css` + `responsive.css` are sitewide base styles; every other CSS/JS file is scoped to one page or one shared component (its own class prefix, e.g. `.gh-*` for Hire Our Graduates, `.alu-*` for Alumni, `.aic-*` for AI Bootcamp).

## Navigation

Primary nav + utility bar (consistent across all pages): Home, About, Admissions, Programmes, AI Bootcamps, Student Life, Hire our Graduates, Corporate Training, Partner with Us, Alumni Registration, Vacancies, Apply/Full Scholarship, Contact. Verified: 0 broken links across all 58 pages.

## Forms

| Form | Page | Status |
|---|---|---|
| Scholarship Application Wizard | `apply.html` | Backend required (has a real but unconfirmed `fetch()` call already) |
| AI Bootcamp Apply | `ai-bootcamp.html` | Backend required (frontend-only fake success today) |
| Alumni Register | `alumni.html` | Backend required (frontend-only fake success today) |
| Contact Us | `contact.html` | Backend required (no JS at all today) |
| Corporate Training Consultation | `corporate-training.html` | Backend required (frontend-only fake success today) |
| Request Graduate Profile | `graduate-hire.html` | Backend required (frontend-only fake success today) |
| Partner With Us | `partner-with-us.html` | Backend required (frontend-only fake success today) |
| Newsletter signup | 10 pages | Backend required (no JS at all, inconsistently placed) |

Full field-by-field detail: `BACKEND-AUDIT-AND-PLAN.md` §1.2.

## Backend Preparation

See `BACKEND-AUDIT-AND-PLAN.md` for the full plan. In short: 12 proposed database tables, a REST API surface for programmes/applications/alumni/graduates/partners/contact/newsletter/vacancies/news plus an admin API, Flask recommended as the backend framework, and a phased roadmap (Programmes data model → Core public forms → Admin dashboard → Hardening → optional CMS-ification of the 26 static school pages).

## Known Issues (see cleanup report §J for full detail)

- `assets/images/gallery-2026/` (~20 real photos) exists but is wired into no page — needs a decision (use it, or archive it).
- `hero-template.html` and `course-detail.html` are orphaned-but-intact legacy pages, kept as-is pending your call.
- `schools-dashboard.css` is active on `courses.html` but its JS counterpart is missing — possible incomplete feature.
- Footer social media icons need real URLs (currently `#` placeholders on every page).
- 1 duplicate `id` (`abWaveGrad` on `about.html`, decorative, low risk).
- `about.html` and `graduate-hire.html` use `<h2>` rather than `<h1>` for their hero headline — flagged rather than changed, to avoid any risk of an unintended visual change from a tag-driven style cascade.
- Visual/responsive regression testing needs a real browser pass — this cleanup was code/text-based only.
