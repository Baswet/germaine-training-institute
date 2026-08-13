# EarnCash — Germaine Institute Student Referral Platform

A referral platform for Germaine Institute: students share a referral
link, friends enroll in a real course, and once Germaine's staff verify
that tuition was actually paid, the referrer earns a real commission.

This EarnCash project is now bundled inside the main Germaine Institute
website as a subfolder (`GermaineInstitute/EarnCash/`), and the site's
"Earn Cash Fast" navigation link on every page points to the EarnCash
landing page at `EarnCash/frontend/pages/index.html`. The EarnCash
landing page also links back to the main site.

## What changed from the original project

The project this was built from had two unfinished, conflicting copies
of the frontend, an unauthenticated backend, and — most importantly —
a commission system that could be triggered by anyone at any time with
no connection to a real payment. That's the structure of a pyramid/
Ponzi scheme, so it was not something we could finish as originally
specced. This version instead:

- Added `courses` and `enrollments` tables so there's a real product
  (tuition) behind every referral.
- Commissions are created in exactly one place in the code —
  `backend/routes/admin.py::verify_enrollment_payment` — and only
  after an admin confirms a real tuition payment was received.
- Added JWT authentication to every route that touches personal data
  or money (the original had none).
- Fixed the broken/duplicate script includes, the empty `css/`
  folder pages were linking to, and consolidated two half-built
  frontends into one working structure.

## Project structure

```
EarnCash/
├── backend/
│   ├── app.py                 Flask entrypoint, blueprint registration
│   ├── config.py               Loads settings from .env
│   ├── database.py             MySQL connection pool
│   ├── requirements.txt
│   ├── .env.example             Copy to .env and fill in
│   ├── routes/                 auth, users, courses, referrals,
│   │                            withdrawals, notifications, admin
│   ├── models/                 Thin data-access helpers per table
│   └── utils/                  JWT/auth decorators, validation helpers
│
├── database/
│   └── earncash.sql             Full schema + seed admin + seed courses
│
└── frontend/
    ├── pages/                   index, register, login, dashboard,
    │                            courses, referrals, withdrawal,
    │                            notifications, profile, admin-login,
    │                            admin
    ├── css/                     Existing glass/pink theme, unchanged
    ├── js/                      config.js + one script per page
    └── assets/                  (images/icons — add your own)
```

## 1. Prerequisites

- Python 3.10+
- MySQL 8+ (or MariaDB 10.5+)
- Any static file server for the frontend (a one-line Python command
  works fine for development — see below)

## 2. Database setup

```bash
mysql -u root -p < database/earncash.sql
```

This creates the `earncash` database, all tables, one seeded admin
account, and eight sample Germaine Institute courses.

**Default admin login:**
- Email: `admin@germaine.ac.ke`
- Password: `ChangeMe123!`

Log in and change this password immediately — there's no "forgot
password" flow yet, so if you lose it you'll need to update the
`password_hash` column directly or re-run the seed insert.

## 3. Backend setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
```

Edit `.env`:
- `DB_PASSWORD` — your MySQL password
- `JWT_SECRET` — generate one with:
  `python3 -c "import secrets; print(secrets.token_hex(32))"`
- `FRONTEND_ORIGIN` — must exactly match the URL you serve the
  frontend from (see step 4)

Run it:

```bash
python app.py
```

The API is now live at `http://127.0.0.1:5000`. Visiting `/` should
return `{"message": "EarnCash Backend API Running", "status": "online"}`.

## 4. Frontend setup

The frontend is plain HTML/CSS/JS — no build step — but it must be
served over `http://`, not opened as a `file://` path, or the API
requests will be blocked by the browser.

Because the "Earn Cash Fast" link on the main Germaine site and the
"Germaine Institute" link on the EarnCash landing page are relative
paths between the two projects, serve the **whole combined folder**
(`GermaineInstitute/`, one level above this `EarnCash/` folder) as a
single static site rather than serving `EarnCash/frontend/` alone:

```bash
cd GermaineInstitute        # the folder containing both index.html and EarnCash/
python3 -m http.server 5500
```

Then open:
- Main site: `http://127.0.0.1:5500/index.html`
- EarnCash: `http://127.0.0.1:5500/EarnCash/frontend/pages/index.html`
  (or just click "Earn Cash Fast" in the main site's nav bar)

If you serve the frontend from a different port/host, update:
- `FRONTEND_ORIGIN` in `backend/.env` (e.g. `http://127.0.0.1:5500`)
- `API_BASE` in `frontend/js/config.js` (if the backend also moves)

## 5. How a commission actually gets created

1. A user registers, optionally with a referral code from a friend's
   link (`register.html?ref=CODE`). This is stored on their account
   but **creates no money yet**.
2. They browse `courses.html` and enroll in a course. This creates an
   `enrollments` row with `payment_status = 'unpaid'` — still no
   money.
3. The student pays tuition to Germaine directly (M-Pesa, bank, or in
   person) — outside this app, the same way tuition is paid today.
4. An admin logs into `admin.html` and opens **Pending Tuition
   Payments**, confirms the amount actually received against a real
   receipt/statement, and clicks Verify.
5. Only at this point — server-side, inside
   `verify_enrollment_payment` — does the system check whether the
   enrollment is now fully paid and whether the student was referred.
   If both are true, it creates one `referral_commissions` row, credits
   the referrer's wallet, and logs a transaction and notification.

There is no path in the code from "someone signed up" to "wallet
balance goes up." Signups and referrals-of-referrals are never paid.

## 6. Business rules you may want to tune

In `backend/.env`:
- `COMMISSION_RATE` — fraction of tuition paid out as commission
  (default `0.10` = 10%)
- `MIN_WITHDRAWAL_AMOUNT` — smallest withdrawal a user can request
  (default `500`)

## 7. Before this goes anywhere near production

This is a working local/demo build. Before real users and real money
touch it:

- Put the Flask app behind HTTPS (nginx/gunicorn + TLS), not the Flask
  dev server.
- Rotate `JWT_SECRET` and never commit `.env`.
- Add rate limiting on `/api/auth/login` and `/api/auth/register`.
- Add real M-Pesa/bank reconciliation (e.g. Daraja API callbacks)
  instead of manual admin entry, if volume grows.
- Add database backups and a password-reset flow.
- Have someone review the referral/commission flow against Kenyan
  consumer protection and financial regulations before processing
  real withdrawals — this document is not legal advice.
