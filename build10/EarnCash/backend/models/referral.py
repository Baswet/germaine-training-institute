"""
Data-access functions for referrals and referral_commissions.
Commission rows are only ever inserted from
routes/admin.py::verify_enrollment_payment, after a real tuition
payment has been confirmed — never from a user-facing endpoint.
"""


def get_referred_users(cursor, referrer_id):
    cursor.execute(
        """
        SELECT id, fullname, email, created_at
        FROM users
        WHERE referred_by=%s
        ORDER BY created_at DESC
        """,
        (referrer_id,),
    )
    return cursor.fetchall()


def get_commissions_for_referrer(cursor, referrer_id):
    cursor.execute(
        """
        SELECT
            rc.id, rc.referred_user_id, rc.commission_amount, rc.status, rc.created_at,
            u.fullname AS referred_user_name,
            c.name AS course_name
        FROM referral_commissions rc
        JOIN users u ON rc.referred_user_id = u.id
        JOIN enrollments e ON rc.enrollment_id = e.id
        JOIN courses c ON e.course_id = c.id
        WHERE rc.referrer_id=%s
        ORDER BY rc.created_at DESC
        """,
        (referrer_id,),
    )
    return cursor.fetchall()


def create_commission(cursor, referrer_id, referred_user_id, enrollment_id, amount):
    cursor.execute(
        """
        INSERT INTO referral_commissions
            (referrer_id, referred_user_id, enrollment_id, commission_amount)
        VALUES (%s, %s, %s, %s)
        """,
        (referrer_id, referred_user_id, enrollment_id, amount),
    )
    return cursor.lastrowid
