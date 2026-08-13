"""
cPanel / Phusion Passenger entry point.

cPanel's "Setup Python App" tool (and Passenger generally) looks for a
file named exactly `passenger_wsgi.py` at the application's root
directory and imports an `application` callable from it — this is the
ONE file that convention requires; everything else in this project is
unaffected by it. It does not replace wsgi.py (still used for local
`python wsgi.py` / `flask run`) — this file exists purely so cPanel has
the entry point it looks for.

Setup on cPanel:
  1. cPanel -> Setup Python App -> Create Application
       - Python version: 3.10+ (whatever the host offers closest to
         the version this project was built/tested against)
       - Application root: the folder this file lives in
         (germaine-backend/)
       - Application URL: the subdomain/path this API should answer on
         (e.g. api.yourdomain, or a path if reverse-proxied)
       - Application startup file: passenger_wsgi.py
       - Application Entry point: application
  2. Use the "Run Pip Install" button (or the venv activate command
     cPanel shows you) against requirements.txt — do NOT install
     pytest/testing-only deps in production if you want to trim it
     down; they are harmless either way, just unused.
  3. Set the environment variables listed in .env.production.example
     via cPanel's "Environment Variables" section for this app (or a
     real .env file placed next to this one — either works, since
     app/__init__.py calls load_dotenv() before reading config).
  4. Run the migration command from DEPLOYMENT.md's "Database
     Migration" section via cPanel's Terminal (or SSH), using the
     venv cPanel created for this app.
  5. Restart the app from the Setup Python App screen so it picks up
     the new environment variables / migrated schema.

This file intentionally contains no logic of its own beyond importing
the already-tested app factory — there is nothing here that needs its
own tests.
"""

from app import create_app

application = create_app()
