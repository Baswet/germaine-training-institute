from flask import Blueprint, jsonify, request, g

from database import get_db
from models import user as user_model
from utils.security import token_required

courses = Blueprint("courses", __name__)


# ======================================
# LIST ACTIVE COURSES
# ======================================
@courses.route("", methods=["GET"])
def list_courses():
    with get_db() as (conn, cursor):
        cursor.execute(
            "SELECT id, name, category, tuition_fee, description FROM courses WHERE is_active=TRUE ORDER BY category, name"
        )
        return jsonify(cursor.fetchall())


# ======================================
# ENROLL IN A COURSE
# Creates an unpaid enrollment. Tuition is paid offline (bank/
# M-Pesa/at the bursar's office) and later verified by an admin,
# which is what triggers any referral commission.
# ======================================
@courses.route("/enroll", methods=["POST"])
@token_required
def enroll():
    data = request.get_json(silent=True) or {}
    course_id = data.get("course_id")
    if not course_id:
        return jsonify({"error": "course_id is required"}), 400

    student_id = g.current_user_id

    with get_db() as (conn, cursor):
        cursor.execute("SELECT * FROM courses WHERE id=%s AND is_active=TRUE", (course_id,))
        course = cursor.fetchone()
        if not course:
            return jsonify({"error": "Course not found"}), 404

        student = user_model.find_by_id(cursor, student_id)

        cursor.execute(
            """
            INSERT INTO enrollments (student_id, course_id, referred_by, amount_due)
            VALUES (%s, %s, %s, %s)
            """,
            (student_id, course_id, student["referred_by"], course["tuition_fee"]),
        )
        conn.commit()

        return jsonify({
            "message": "Enrollment created. Complete tuition payment to activate your course.",
            "enrollment_id": cursor.lastrowid,
            "amount_due": str(course["tuition_fee"]),
        }), 201


# ======================================
# MY ENROLLMENTS
# ======================================
@courses.route("/my-enrollments", methods=["GET"])
@token_required
def my_enrollments():
    with get_db() as (conn, cursor):
        cursor.execute(
            """
            SELECT e.id, e.amount_due, e.amount_paid, e.payment_status, e.created_at,
                   c.name AS course_name, c.category
            FROM enrollments e
            JOIN courses c ON e.course_id = c.id
            WHERE e.student_id=%s
            ORDER BY e.created_at DESC
            """,
            (g.current_user_id,),
        )
        return jsonify(cursor.fetchall())
