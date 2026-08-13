from flask import Blueprint, jsonify, g

from database import get_db
from utils.security import token_required

notifications = Blueprint("notifications", __name__)


# ======================================
# GET MY NOTIFICATIONS
# ======================================
@notifications.route("/<int:user_id>", methods=["GET"])
@token_required
def get_notifications(user_id):
    if g.current_user_role != "admin" and g.current_user_id != user_id:
        return jsonify({"error": "You may only access your own data"}), 403

    with get_db() as (conn, cursor):
        cursor.execute(
            "SELECT * FROM notifications WHERE user_id=%s ORDER BY created_at DESC",
            (user_id,),
        )
        return jsonify(cursor.fetchall())


# ======================================
# MARK AS READ
# ======================================
@notifications.route("/read/<int:notification_id>", methods=["PUT"])
@token_required
def mark_read(notification_id):
    with get_db() as (conn, cursor):
        cursor.execute("SELECT user_id FROM notifications WHERE id=%s", (notification_id,))
        note = cursor.fetchone()
        if not note:
            return jsonify({"error": "Notification not found"}), 404
        if g.current_user_role != "admin" and g.current_user_id != note["user_id"]:
            return jsonify({"error": "You may only modify your own notifications"}), 403

        cursor.execute("UPDATE notifications SET status='read' WHERE id=%s", (notification_id,))
        conn.commit()
        return jsonify({"message": "Notification updated"})


# ======================================
# DELETE NOTIFICATION
# ======================================
@notifications.route("/delete/<int:notification_id>", methods=["DELETE"])
@token_required
def delete_notification(notification_id):
    with get_db() as (conn, cursor):
        cursor.execute("SELECT user_id FROM notifications WHERE id=%s", (notification_id,))
        note = cursor.fetchone()
        if not note:
            return jsonify({"error": "Notification not found"}), 404
        if g.current_user_role != "admin" and g.current_user_id != note["user_id"]:
            return jsonify({"error": "You may only delete your own notifications"}), 403

        cursor.execute("DELETE FROM notifications WHERE id=%s", (notification_id,))
        conn.commit()
        return jsonify({"message": "Notification deleted"})
