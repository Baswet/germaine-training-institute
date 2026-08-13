"""
EarnCash notification routes — ported from
build10/EarnCash/backend/routes/notifications.py.

Registered at /api/earncash/notifications/... (see app/__init__.py).
"""

from flask import jsonify, g

from app.extensions import db
from app.models import EarnCashNotification
from app.utils.earncash_jwt import token_required
from app.blueprints.earncash import earncash_bp


# ======================================
# GET MY NOTIFICATIONS
# ======================================
@earncash_bp.route("/notifications/<int:user_id>", methods=["GET"])
@token_required
def get_notifications(user_id):
    if g.earncash_user_role != "admin" and g.earncash_user_id != user_id:
        return jsonify({"error": "You may only access your own data"}), 403

    notes = (
        EarnCashNotification.query.filter_by(user_id=user_id)
        .order_by(EarnCashNotification.created_at.desc())
        .all()
    )
    return jsonify([n.to_dict() for n in notes])


# ======================================
# MARK AS READ
# ======================================
@earncash_bp.route("/notifications/read/<int:notification_id>", methods=["PUT"])
@token_required
def mark_read(notification_id):
    note = db.session.get(EarnCashNotification, notification_id)
    if not note:
        return jsonify({"error": "Notification not found"}), 404
    if g.earncash_user_role != "admin" and g.earncash_user_id != note.user_id:
        return jsonify({"error": "You may only modify your own notifications"}), 403

    note.status = "read"
    db.session.commit()
    return jsonify({"message": "Notification updated"})


# ======================================
# DELETE NOTIFICATION
# ======================================
@earncash_bp.route("/notifications/delete/<int:notification_id>", methods=["DELETE"])
@token_required
def delete_notification(notification_id):
    note = db.session.get(EarnCashNotification, notification_id)
    if not note:
        return jsonify({"error": "Notification not found"}), 404
    if g.earncash_user_role != "admin" and g.earncash_user_id != note.user_id:
        return jsonify({"error": "You may only delete your own notifications"}), 403

    db.session.delete(note)
    db.session.commit()
    return jsonify({"message": "Notification deleted"})
