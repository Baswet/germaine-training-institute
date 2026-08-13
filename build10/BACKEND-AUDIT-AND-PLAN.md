derer# Germaine Training Institute — Backend Audit & Development Plan

**Date:** August 11, 2026
**Scope:** `build10/` frontend (58 real HTML pages + shared assets). No code was written. No database was created. The frontend was not redesigned.

**A note on `EarnCash/`:** a separate, already-built referral/commission platform lives inside `build10/EarnCash/` with its own Flask backend and MySQL schema (see `AUDIT_REPORT.md` at the project root for its own prior audit, dated July 22 2026). Per your instruction, it is documented here as an existing, independent system and is **excluded** from the backend plan below — the plan that follows is scoped entirely to Germaine's own institutional systems.

---

## 1. Frontend Audit

### 1.1 Page inventory (58 pages)

| Group | Pages | Notes |
|---|---|---|
| Core | `index.html`, `about.html`, `contact.html`, `news.html` | |
| Admissions | `admissions.html`, `apply.html` | `apply.html` is the real "Apply for a Full Scholarship" multi-step wizard |
| Programmes hub | `courses.html` | Catalogue/landing page for all academic schools |
| Academic school/department pages | 26 `courses-*.html` pages (Agriculture, Business & Commerce, Computing & IT, Cosmetology/Fashion, Engineering & Technology, Health Sciences, Hospitality & Tourism, 4 language pages, Law, Mass Comm & Journalism, Social Sciences, Teachers Training, Virtual Learning, Short Courses index + 6 short-course subpages) | All static HTML, hardcoded content per page |
| AI Bootcamp | `ai-bootcamp.html`, `ai-bootcamp-courses.html` (hub), 14 `ai-course-*.html` detail pages | Data-driven from `assets/js/ai-courses-data.js` — the one real content model already in this project |
| Student life | `campus.html` | |
| Alumni | `alumni.html` | Register form |
| Graduates (employer-facing) | `graduate-hire.html` | Request Graduate Profile modal |
| Partners | `partner-with-us.html`, `corporate-training.html` | |
| Careers | `vacancies.html` | |
| Legacy/orphaned (not linked from nav, harmless) | `hero-template.html`, `course-detail.html` (+ its own `courses-data.js`/`course-detail.js`) | Predates the `ai-course-*` system; nothing currently links to it. Flagged for your decision — see Cleanup Report. |

### 1.2 Forms found (7 real forms + 10 unwired newsletter boxes)

| Form | Page | Fields (essential) | Current behavior |
|---|---|---|---|
| Scholarship Application Wizard | `apply.html` (`#apForm`, multi-step) | Mode, school, programme, full name, phone, email, national ID, DOB, gender, county, education level, KCSE grade, terms consent | **Actually attempts a real POST** to `https://www.germaineinstitute.com/application/clients/add` (fire-and-forget, `no-cors`, ignores the response) — see §1.5 |
| AI Bootcamp Apply | `ai-bootcamp.html` (`#aiApplyForm`) | Name, email, phone, programme interest | JS `preventDefault()` → shows a fake success state. No network call. |
| Alumni Register | `alumni.html` (`#alumniForm`) | Full name, email, phone/WhatsApp, programme, graduation year, organisation (optional), stay-connected pills, consent | Same fake-success pattern, no network call |
| Contact Us | `contact.html` (`#contact-form`) | Name, email, subject, message | **No JS handler at all** — plain HTML form, currently does nothing on submit |
| Consultation Request (Corporate Training) | `corporate-training.html` (`#cmForm`, modal) | Company, contact name, email, phone, training need | Fake-success pattern; code comment explicitly marks where a real `fetch()` POST goes |
| Request Graduate Profile | `graduate-hire.html` (`#gpForm`, modal) | Employer name, company, email, phone, role needed, message | Fake-success pattern; same "wire a real fetch() here" comment |
| Partner With Us | `partner-with-us.html` (`#pwForm`) | Organisation, contact name, email, phone, partnership type, message | Fake-success pattern; same "wire a real fetch() here" comment |
| Newsletter signup | 10 pages (`.newsletter-form`, no `id`) — About, Admissions, Apply, course-detail, 4 courses-* pages, News | Email only | **Zero JS anywhere in the project touches `.newsletter-form`.** Plain submit, does nothing. Inconsistently present (only 10 of 58 pages have it). |

**Everything above is BACKEND REQUIRED.** Zero forms currently persist data anywhere. The scholarship wizard is the one exception with real *intent* (a live `fetch()` call), but it doesn't wait for or check the response, so it cannot currently be trusted to confirm a submission succeeded.

### 1.3 Every CTA that should eventually perform a backend action

- Apply Scholarship Now (sitewide sticky button + hero CTAs) → `apply.html#applyWizard`
- Hire our Graduates → `graduate-hire.html` → Request Graduate Profile modal
- Partner with Us → `partner-with-us.html` form
- Alumni Registration → `alumni.html` form
- Corporate Training → Schedule/Request Consultation modal
- AI Bootcamp → Apply Now (per-programme, `#aicApply` anchor toggle)
- Vacancies → currently browse-only, no application flow exists yet (see §2, Recruitment note)
- Newsletter subscribe (10 pages)
- Contact Us submit

### 1.4 Navigation

Primary nav + utility bar (from `index.html`, consistent site-wide): Home, About, Admissions, Programmes (courses.html + 26 school pages), AI Bootcamps, Student Life, Hire our Graduates, Corporate Training, Partner with Us, Alumni Registration, Vacancies, Full Scholarship (Apply), Contact, phone/email links, Earn Cash Fast (→ separate EarnCash app). All resolved correctly — see Cleanup Report §C for the full link audit (0 broken links found).

### 1.5 Programme/course data sources

Two parallel content models exist:

1. **`assets/js/ai-courses-data.js`** — the only real structured data model in the project. A single JS array of 14 course objects (slug, file, category, title, duration, fees per learning mode, real start dates for most, FAQs, skills, careers). Rendered onto pages by `assets/js/ai-course-detail-renderer.js`. This is the natural template for what a `programmes` database table should look like.
2. **26 `courses-*.html` academic school pages** — 100% hardcoded static HTML. No JSON/JS data file backs these. Programme names, fees (where shown), durations, and intake info are typed directly into each page's markup.

### 1.6 Schools/departments referenced

Business & Commerce, Computing & IT / Informatics, Cosmetology/Fashion & Design, Engineering & Technology, Health Sciences, Hospitality & Tourism, Languages (Chinese/English/French/German), Law, Mass Communication & Journalism, Social Sciences, Teachers Training College, Virtual Learning, Agriculture, plus short-course tracks (Beauty Therapy, Hair Dressing, Building & Construction, Catering & Accommodation, Electrical & Electronics, Mechanical & Motor Mechanics, Medical). All currently exist only as page content, not as rows in any data store.

### 1.7 Hardcoded data that should eventually come from a database

- All 26 academic school pages' programme lists, fees, durations, intake dates
- Partner/accreditation logos and names (NITA, TVETA, KNEC, KASNEB — `graduate-hire.html`, `partner-with-us.html`)
- Testimonials (AI Bootcamp, elsewhere)
- Vacancies listings (`vacancies.html`) — currently static job postings
- News articles (`news.html`)
- Gallery/Student Life photo captions

### 1.8 Image/file upload requirements

None currently implemented in the frontend. Future needs, based on the forms above: scholarship applicant document uploads (ID copy, KCSE certificate), employer-requested graduate CVs/portfolios (Request Graduate Profile flow), partner organisation logos (Partner With Us), admin-side programme/vacancy imagery.

### 1.9 Authentication requirements

None exist today — the entire site is public/anonymous. Needed: an admin authentication layer for the future dashboard (see §6). No student/alumni/employer login exists in the frontend today, but the Alumni and Graduate-employer flows would benefit from optional accounts down the line (not required for MVP).

### 1.10 Sections needing an admin dashboard

Admissions/scholarship applications queue, alumni directory, graduate-profile requests from employers, partner enquiries, corporate training consultation requests, contact messages, newsletter subscriber list, vacancies CRUD, news CRUD, and (longer-term) programme/school/fee CRUD to replace the hardcoded HTML pages.

### 1.11 API/data dependencies

- The scholarship wizard already targets `https://www.germaineinstitute.com/application/clients/add` — worth confirming with you whether this endpoint is live, planned, or a placeholder domain, since it directly affects the API design in §4.
- Font Awesome is loaded from `cdnjs.cloudflare.com` (external CDN, no backend implication).
- No other external APIs are called anywhere in the Germaine pages.

### 1.12 Where JavaScript currently simulates functionality

`alumni.js`, `ai-bootcamp.js`, `consultation-modal.js`, `graduate-profile-form.js`, `partner-with-us.js` all follow the same pattern: `e.preventDefault()` → hide the form → show a success message — with no network call. `apply-wizard.js` is the one exception (real `fetch()`, but ignores the response). `contact.html`'s form has no JS at all.

### 1.13 External services currently in use

Font Awesome (CDN), Google Fonts (Poppins/Open Sans, per the brand system), WhatsApp click-to-chat link (`wa.me/254719488112`), `tel:`/`mailto:` links. No analytics, no payment gateway, no CRM integration found anywhere in the Germaine pages.

---

## 2. Backend Feature List

**Admissions**
Programme applications (from the existing scholarship wizard's field set), application records, applicant information, application status (received → under review → offered → enrolled/declined), application management (admin review queue).

**Scholarships**
Reuses the Admissions data model 1:1 today — `apply.html` *is* the scholarship application. If a non-scholarship general application is wanted later, the same table can hold both with an `application_type` column.

**Alumni**
Alumni registration (from `alumni.html`'s real field set), alumni profiles, engagement preferences (the Networking/Mentorship/Events/Career Opportunities pills already in the form), alumni communication (opt-in consent already captured in the form).

**Graduates**
Request Graduate Profile (employer-submitted, from `graduate-hire.html`), graduate profiles (future — no graduate-facing submission form exists yet, so this starts as admin-entered data), employer requests queue, graduate database.

**Partners**
Partner registration/enquiry (from `partner-with-us.html`'s form), corporate training consultation requests (from `corporate-training.html`'s form — could share one `partner_enquiries` table with a `type` column), partner records.

**Programmes**
Schools, departments, programmes, programme details (duration, learning modes, fees — modelled directly on `ai-courses-data.js`'s existing shape), programme categories.

**Communication**
Contact enquiries (`contact.html`), newsletter subscribers (10 unwired forms), email notifications (confirmation to applicant + alert to admissions staff on every submission type), administrative notifications.

**Administration**
Admin authentication, dashboard, user roles (e.g. Super Admin, Admissions Officer, Content Editor), CRUD for programmes/vacancies/news, application/enquiry management across all the queues above.

**Vacancies (not in your list, but present in the frontend)**
`vacancies.html` currently lists static job postings with no application flow — flagging this as a probable near-term addition once the core modules above exist.

---

## 3. Database Architecture

Only tables the actual frontend content justifies — nothing speculative.

| Table | Purpose | Key fields | PK | Relationships |
|---|---|---|---|---|
| `schools` | The ~13 academic schools/departments | name, slug, description | `id` | has many `programmes` |
| `programmes` | Every programme across academic schools + AI Bootcamp | school_id (nullable for AI Bootcamp), name, slug, category, duration, level, overview | `id` | belongs to `schools`; has many `programme_modes` |
| `programme_modes` | Learning-mode variants (Full-time Hybrid/Remote, Part-time) — mirrors `ai-courses-data.js`'s `modes` array exactly | programme_id, label, duration, fee, start_date, schedule | `id` | belongs to `programmes` |
| `applications` | Scholarship/programme applications (from `apply.html`) | full_name, phone, email, national_id, dob, gender, county, education_level, kcse_grade, programme_id, status, submitted_at | `id` | belongs to `programmes`; has many `application_documents` |
| `application_documents` | Uploaded ID/certificate files per application | application_id, file_path, doc_type, uploaded_at | `id` | belongs to `applications` |
| `alumni` | Alumni registrations (from `alumni.html`) | full_name, email, phone, programme_id, graduation_year, organisation, engagement_interests (JSON/array), consent, registered_at | `id` | belongs to `programmes` |
| `graduate_profile_requests` | Employer requests (from `graduate-hire.html`) | employer_name, company, email, phone, role_needed, message, status, submitted_at | `id` | none required for MVP |
| `partner_enquiries` | Partner With Us + Corporate Training consultation requests | organisation, contact_name, email, phone, enquiry_type, message, status, submitted_at | `id` | none required for MVP |
| `contact_messages` | Contact Us submissions | name, email, subject, message, submitted_at, status | `id` | none |
| `newsletter_subscribers` | The 10 unwired newsletter boxes | email, subscribed_at, active | `id` | none |
| `vacancies` | Job postings (currently hardcoded in `vacancies.html`) | title, department, description, closing_date, is_active | `id` | none for MVP |
| `news_articles` | News page content (currently hardcoded) | title, slug, body, published_at, is_published | `id` | none |
| `admin_users` | Admin dashboard logins | name, email, password_hash, role, created_at | `id` | has many `admin_activity_logs` (optional, phase 2) |

That's 12 tables. Deliberately excluded: a separate `scholarships` table (the frontend has exactly one application flow — splitting it now would be speculative), any `students`/`courses_enrolled` table (no enrolment/LMS functionality exists in the frontend), a `graduates` self-service table (no graduate-facing submission form exists — profiles start as admin-entered rows in a future phase, not a v1 requirement).

---

## 4. API Architecture

```
# Programmes (public read)
GET    /api/schools
GET    /api/schools/:id
GET    /api/programmes
GET    /api/programmes/:id
GET    /api/programmes/:id/modes

# Admissions / Scholarship
POST   /api/applications
GET    /api/applications/:id            (applicant status check, if desired)
POST   /api/applications/:id/documents

# Alumni
POST   /api/alumni

# Graduates
POST   /api/graduate-profile-request

# Partners
POST   /api/partner-enquiries

# Communication
POST   /api/contact
POST   /api/newsletter/subscribe

# Vacancies / News (public read)
GET    /api/vacancies
GET    /api/news

# Admin (auth required)
POST   /api/admin/login
GET    /api/admin/applications
PATCH  /api/admin/applications/:id/status
GET    /api/admin/alumni
GET    /api/admin/graduate-requests
GET    /api/admin/partner-enquiries
GET    /api/admin/contact-messages
POST   /api/admin/vacancies
PUT    /api/admin/vacancies/:id
DELETE /api/admin/vacancies/:id
POST   /api/admin/news
PUT    /api/admin/news/:id
DELETE /api/admin/news/:id
```

Not implemented yet — this is the planning list only.

---

## 5. Technology Recommendation

| | Flask | Django | Node.js/Express |
|---|---|---|---|
| Fit for a mostly-static site adding a moderate number of form-backed endpoints | Strong — lightweight, no forced structure for content you don't have (no CMS-scale needs yet) | Heavier than needed out of the gate; its batteries (ORM, admin, auth) are valuable but add a learning curve for a first backend | Comparable to Flask in weight; fine choice, but the rest of this stack (and any future teammate) benefits from Python being one language across backend + any data/reporting scripts |
| Admin dashboard | Build with Flask-Admin or a small custom dashboard — moderate effort | **Django Admin is free and immediate** — this is Django's strongest card here | No first-party admin scaffold; would be hand-built same as Flask |
| Auth | Flask-Login / Flask-JWT-Extended — simple, sufficient for one `admin_users` table and a handful of roles | Django's built-in auth is more than this project currently needs (no public user accounts yet) | Passport.js or hand-rolled JWT — comparable effort to Flask |
| Database requirements | 12 straightforward relational tables, clear FKs — no exotic query needs | Same fit, ORM is more opinionated | Same fit via Sequelize/Prisma |
| Future scalability | Scales fine for this project's realistic size (a training institute's admissions/alumni/partner workload, not a high-traffic consumer app) | Also scales fine; more overhead if the project stays this size | Also fine |
| Ease of maintenance for a static-HTML-first project like this | **Best fit** — Flask's minimalism matches a project that's 58 static HTML pages plus a handful of form endpoints; you're not fighting a full-stack framework's opinions to keep the existing frontend as-is | Django wants to own routing/templating conventions that would compete with the existing hand-built HTML | Comparable maintenance burden to Flask; matters most if your team is more comfortable in JS than Python |

**Recommendation: Flask.** The project's actual shape — a hand-crafted static frontend (not a Django-templated one) plus roughly a dozen form-backed endpoints and a moderate admin dashboard — matches Flask's minimal-but-extensible profile better than Django's all-in-one conventions or Node's need to hand-build most of the same scaffolding Flask already offers via extensions. If a fully free, zero-effort admin panel matters more to you than staying minimal, Django is the honest alternative — flag it if you'd rather have that trade-off.

### Recommended Flask project structure

```
germaine-backend/
├── app/
│   ├── __init__.py              # app factory
│   ├── config.py                # Config classes, reads from .env
│   ├── extensions.py            # db, migrate, jwt, mail, limiter instances
│   ├── models/
│   │   ├── __init__.py
│   │   ├── programme.py         # School, Programme, ProgrammeMode
│   │   ├── application.py       # Application, ApplicationDocument
│   │   ├── alumni.py
│   │   ├── graduate.py          # GraduateProfileRequest
│   │   ├── partner.py           # PartnerEnquiry
│   │   ├── communication.py     # ContactMessage, NewsletterSubscriber
│   │   ├── content.py           # Vacancy, NewsArticle
│   │   └── admin_user.py
│   ├── routes/
│   │   ├── programmes.py
│   │   ├── applications.py
│   │   ├── alumni.py
│   │   ├── graduates.py
│   │   ├── partners.py
│   │   ├── communication.py
│   │   ├── vacancies.py
│   │   ├── news.py
│   │   └── admin/
│   │       ├── auth.py
│   │       ├── applications.py
│   │       └── content.py
│   ├── schemas/                 # marshmallow or pydantic request/response validation
│   ├── services/                # email sending, file upload handling
│   └── utils/                   # decorators (admin_required), helpers
├── migrations/                  # Flask-Migrate/Alembic
├── uploads/                     # local file storage (or swap for S3-compatible)
├── tests/
├── .env.example
├── requirements.txt
├── wsgi.py
└── README.md
```

---

## 6. Security Planning

- **Password hashing:** `werkzeug.security` (`pbkdf2:sha256`) or `bcrypt` for `admin_users.password_hash` — never plaintext, never logged.
- **Authentication:** JWT (Flask-JWT-Extended) or server-side sessions for the admin dashboard; public endpoints stay anonymous.
- **Authorization:** role checks (`admin_required`, `super_admin_required` decorators) on every `/api/admin/*` route.
- **Input validation:** schema validation (marshmallow/pydantic) on every POST/PATCH body — reject unexpected fields, enforce types/lengths before touching the database.
- **SQL injection protection:** ORM (SQLAlchemy) with parameterised queries throughout; no raw string-interpolated SQL.
- **XSS protection:** escape all user-submitted content wherever it's later rendered (admin dashboard tables, any public-facing testimonial/news content); set `Content-Security-Policy` headers.
- **CSRF protection:** CSRF tokens on the admin dashboard's own forms if server-rendered; for the public JSON API consumed by the existing static HTML, rely on same-origin + CORS restriction rather than CSRF tokens (standard for token-authenticated JSON APIs).
- **File upload security:** restrict to expected MIME types/extensions (PDF/JPG/PNG for ID and certificate uploads), enforce a max size, store outside the web root or in object storage, generate randomised filenames, virus-scan if feasible.
- **Rate limiting:** Flask-Limiter on `/api/applications`, `/api/contact`, `/api/newsletter/subscribe`, and especially `/api/admin/login` (brute-force protection).
- **Environment variables:** `SECRET_KEY`, `JWT_SECRET`, DB credentials, mail credentials all via `.env` (never committed) with a `.env.example` template, following the same pattern already used in `EarnCash/backend`.
- **Secure database credentials:** dedicated least-privilege DB user for the app (not root), connection pooling, credentials never hardcoded.
- **HTTPS:** required in production; local dev can run plain HTTP behind a reverse proxy that terminates TLS (nginx/Caddy) or behind your hosting platform's managed TLS.

---

## 7. Phased Development Roadmap

**Phase 0 — Foundations**
Flask app factory, config/env setup, database connection, migrations tooling, base project structure above.

**Phase 1 — Programmes data model**
Build `schools`/`programmes`/`programme_modes` tables and seed them from `ai-courses-data.js`'s existing 14 entries (already structured) plus the 26 academic school pages' content (manual data entry, since that content is currently hardcoded HTML with no JSON source). Public read-only API (`GET /api/programmes`, etc.).

**Phase 2 — Core public forms**
`applications` (wire the real scholarship wizard's existing `fetch()` call to a real, confirmed endpoint), `alumni`, `graduate_profile_requests`, `partner_enquiries`, `contact_messages`, `newsletter_subscribers`. Email notifications (confirmation + admin alert) on each.

**Phase 3 — Admin dashboard**
`admin_users` + auth, review/manage queues for every table built in Phase 2, CRUD for `vacancies` and `news_articles`.

**Phase 4 — Hardening & scale**
Rate limiting, file-upload security review, HTTPS/deployment setup, activity logging, backups.

**Phase 5 (optional, future)**
Programme/school CRUD in the admin dashboard so the 26 static academic pages can eventually be rendered from the database instead of hand-edited HTML — a larger effort, worth scoping separately once Phases 1-4 are stable.
