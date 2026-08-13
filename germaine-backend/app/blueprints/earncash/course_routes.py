"""
EarnCash course/enrollment routes — ported from
build10/EarnCash/backend/routes/courses.py.

Registered at /api/earncash/courses... (see app/__init__.py).
"""

from flask import request, jsonify, g

from app.extensions import db
from app.models import EarnCashCourse, EarnCashEnrollment, EarnCashUser
from app.utils.earncash_jwt import token_required
from app.blueprints.earncash import earncash_bp


# ======================================
# LIST ACTIVE COURSES
# ======================================
@earncash_bp.route("/courses", methods=["GET"])
def list_courses():
    courses = (
        EarnCashCourse.query.filter_by(is_active=True)
        .order_by(EarnCashCourse.category, EarnCashCourse.name)
        .all()
    )
    return jsonify([c.to_dict() for c in courses])


# ======================================
# ENROLL IN A COURSE
# ======================================
@earncash_bp.route("/courses/enroll", methods=["POST"])
@token_required
def enroll():
    data = request.get_json(silent=True) or {}
    course_id = data.get("course_id")
    if not course_id:
        return jsonify({"error": "course_id is required"}), 400

    student_id = g.earncash_user_id

    course = EarnCashCourse.query.filter_by(id=course_id, is_active=True).first()
    if not course:
        return jsonify({"error": "Course not found"}), 404

    student = db.session.get(EarnCashUser, student_id)

    enrollment = EarnCashEnrollment(
        student_id=student_id,
        course_id=course_id,
        referred_by=student.referred_by,
        amount_due=course.tuition_fee,
    )
    db.session.add(enrollment)
    db.session.commit()

    return jsonify({
        "message": "Enrollment created. Complete tuition payment to activate your course.",
        "enrollment_id": enrollment.id,
        "amount_due": str(course.tuition_fee),
    }), 201


# ======================================
# MY ENROLLMENTS
# ======================================
@earncash_bp.route("/courses/my-enrollments", methods=["GET"])
@token_required
def my_enrollments():
    enrollments = (
        EarnCashEnrollment.query.filter_by(student_id=g.earncash_user_id)
        .order_by(EarnCashEnrollment.created_at.desc())
        .all()
    )
    return jsonify([
        {
            "id": e.id,
            "amount_due": str(e.amount_due),
            "amount_paid": str(e.amount_paid),
            "payment_status": e.payment_status,
            "created_at": e.created_at.isoformat() if e.created_at else None,
            "course_name": e.course.name if e.course else None,
            "category": e.course.category if e.course else None,
        }
        for e in enrollments
    ])
