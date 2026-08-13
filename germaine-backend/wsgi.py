"""
WSGI / local-dev entry point.

Running `python wsgi.py` or `flask --app wsgi run` starts the app
locally against whatever FLASK_ENV/DATABASE_URL is set in the
environment (see .env.example). This file does not start a database,
run migrations, or seed data on its own — it only boots the Flask app.
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
