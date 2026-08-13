from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from routes.auth import auth
from routes.users import users
from routes.courses import courses
from routes.referrals import referrals
from routes.withdrawals import withdrawals
from routes.notifications import notifications
from routes.admin import admin

Config.validate()

app = Flask(__name__)

# Only allow the configured frontend origin, with credentials support
# turned off since we use bearer tokens (not cookies).
CORS(app, resources={r"/api/*": {"origins": Config.FRONTEND_ORIGIN}})

# ======================================
# REGISTER BLUEPRINTS
# ======================================
app.register_blueprint(auth, url_prefix="/api/auth")
app.register_blueprint(users, url_prefix="/api/users")
app.register_blueprint(courses, url_prefix="/api/courses")
app.register_blueprint(referrals, url_prefix="/api/referrals")
app.register_blueprint(withdrawals, url_prefix="/api/withdrawals")
app.register_blueprint(notifications, url_prefix="/api/notifications")
app.register_blueprint(admin, url_prefix="/api/admin")


# ======================================
# HOME / HEALTH CHECK
# ======================================
@app.route("/")
def home():
    return jsonify({"message": "EarnCash Backend API Running", "status": "online"})


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed"}), 405


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    # Step: was hardcoded to 5000, which collides with germaine-backend
    # (the main Germaine Institute site's Flask app, already running on
    # 5000). EarnCash is a fully separate backend/database from
    # germaine-backend, so instead of fighting over one port, it now runs
    # on its own: 5001. frontend/js/config.js API_BASE was updated to
    # match. germaine-backend is untouched.
    app.run(host="0.0.0.0", port=5001, debug=True)
