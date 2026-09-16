# Germaine Training Institute — website and Flask back end

The public website of Germaine Training Institute (Kenya), plus the Flask + PostgreSQL back end behind its admissions, alumni, enquiry and admin features. I work on this as the institute's web developer.

**Live:** [germaineinstitute.ac.ke](https://germaineinstitute.ac.ke/) · **API health check:** [api.germaineinstitute.ac.ke/api/health](https://api.germaineinstitute.ac.ke/api/health)

![Germaine Training Institute home page](https://baswet.github.io/germaine-home.webp)

## What's in this repository

| Folder | What it is |
|---|---|
| `build10/` | The public website: static HTML, CSS and JavaScript (course catalogue, admissions and scholarship application, alumni, graduate hire, partners, news, vacancies, AI bootcamp page) |
| `germaine-backend/` | Flask application: models, blueprints, services, admin dashboard templates, migrations, tests and deployment files |
| `.github/workflows/deploy-pages.yml` | GitHub Actions workflow that publishes the static site to GitHub Pages |
| `*-REPORT.md` | Working reports written during each phase (redesigns, audits, admin dashboard, production release) |

## Back end at a glance

- **Flask application factory** (`app/__init__.py`) with environment-based configuration.
- **Six blueprints:** `public`, `admissions`, `alumni`, `enquiries`, `earncash` (student referral programme) and `admin`.
- **SQLAlchemy models** for schools, programme categories, programmes, applicants and applications, alumni, graduate-profile requests, contact messages, partner enquiries, news, newsletter subscribers, media assets, editable site content and the referral programme.
- **Services layer** (`app/services/`) for admissions, scholarships, the programme catalogue, CMS content, engagement forms and admin actions.
- **PostgreSQL + Flask-Migrate** — schema changes go through migrations (`migrations/versions/`).
- **Admin dashboard** (Jinja templates in `app/templates/admin/`): applications, alumni, enquiries, graduate-hire requests, academics (schools, categories, programmes), news, newsletter, media library and site content.
- **Admin sign-in** with JWT (PyJWT) and password reset.
- **Tests:** 17 pytest modules in `germaine-backend/tests/` (app factory, config, CORS, health, admissions, catalogue, engagement, CMS, admin dashboard, CLI and more).
- **Deployment:** runs on cPanel through Passenger (`passenger_wsgi.py`); `wsgi.py` and `render.yaml` are included for other hosts. API endpoints are documented in [`germaine-backend/API_DOCS.md`](germaine-backend/API_DOCS.md) and deployment steps in [`germaine-backend/DEPLOYMENT.md`](germaine-backend/DEPLOYMENT.md).

> `germaine-backend/README.md` was written at the scaffolding stage and describes that early step. Since then, migrations were added and the API went live at the address above.

## Added on the live server after this snapshot

This repository was last updated in August 2026. The production deployment has since added, and these are not in this repository yet:

- **Applicant document records** — scholarship letters are generated in the browser and stored on the server with a record of when each one was generated, sent and viewed.
- **Notifications** by email, SMS (Africa's Talking) and WhatsApp (Cloud API), isolated so a failed message never undoes an application or approval.

## Run the back end locally

```bash
cd germaine-backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # set DATABASE_URL, SECRET_KEY and the other values
flask --app wsgi db upgrade
flask --app wsgi run
```

Secrets are read from environment variables. Never commit a real `.env` file.

## Tech

Python · Flask · SQLAlchemy · Flask-Migrate · PostgreSQL · PyJWT · Jinja · pytest · HTML · CSS · JavaScript · GitHub Actions · cPanel / Passenger

---
Maintained by [Emmanuel](https://baswet.github.io) · Kenya
