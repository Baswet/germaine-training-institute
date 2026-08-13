"""
EarnCash blueprint tests — register/login happy paths, negative cases
(duplicate email, invalid email, missing field, invalid password), auth
protection, and a basic dashboard-stats read. Uses the same in-memory
SQLite db_client fixture as every other DB-backed test in this suite
(see tests/conftest.py) — no live PostgreSQL server required.
"""


def _register(client, **overrides):
    payload = {
        "fullname": "Test Student",
        "email": "test.student@example.com",
        "phone": "0712345678",
        "password": "testpass123",
        "referral_code": "",
    }
    payload.update(overrides)
    return client.post("/api/earncash/auth/register", json=payload)


def _login(client, email, password):
    return client.post("/api/earncash/auth/login", json={"email": email, "password": password})


# ======================================
# REGISTER
# ======================================
def test_register_success(db_client):
    resp = _register(db_client)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["message"] == "Account created successfully"
    assert data["referral_code"].startswith("EC")


def test_register_duplicate_email(db_client):
    first = _register(db_client)
    assert first.status_code == 201

    second = _register(db_client)
    assert second.status_code == 409
    assert "already exists" in second.get_json()["error"]


def test_register_invalid_email(db_client):
    resp = _register(db_client, email="not-an-email")
    assert resp.status_code == 400
    assert "valid email" in resp.get_json()["error"]


def test_register_missing_required_field(db_client):
    resp = db_client.post("/api/earncash/auth/register", json={"email": "x@example.com", "password": "testpass123"})
    assert resp.status_code == 400
    assert "fullname" in resp.get_json()["error"]


def test_register_password_too_short(db_client):
    resp = _register(db_client, password="short")
    assert resp.status_code == 400
    assert "8 characters" in resp.get_json()["error"]


def test_register_with_valid_referral_code_links_referrer(db_client):
    referrer_resp = _register(db_client, email="referrer@example.com")
    referral_code = referrer_resp.get_json()["referral_code"]

    referred_resp = _register(db_client, email="referred@example.com", referral_code=referral_code)
    assert referred_resp.status_code == 201

    login_resp = _login(db_client, "referrer@example.com", "testpass123")
    referrer_id = login_resp.get_json()["user"]["id"]

    stats_resp = db_client.get(
        f"/api/earncash/users/stats/{referrer_id}",
        headers={"Authorization": f"Bearer {login_resp.get_json()['token']}"},
    )
    assert stats_resp.status_code == 200
    assert stats_resp.get_json()["total_referrals"] == 1


def test_register_with_invalid_referral_code_still_succeeds(db_client):
    # An unrecognized referral code must not block registration — it's
    # silently ignored (matches the original EarnCash behavior).
    resp = _register(db_client, referral_code="NOTAREALCODE")
    assert resp.status_code == 201


# ======================================
# LOGIN
# ======================================
def test_login_success(db_client):
    _register(db_client)
    resp = _login(db_client, "test.student@example.com", "testpass123")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["token"]
    assert data["user"]["email"] == "test.student@example.com"
    assert data["user"]["role"] == "user"


def test_login_wrong_password(db_client):
    _register(db_client)
    resp = _login(db_client, "test.student@example.com", "wrongpassword")
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "Invalid email or password"


def test_login_unknown_email(db_client):
    resp = _login(db_client, "nobody@example.com", "testpass123")
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "Invalid email or password"


def test_login_missing_field(db_client):
    resp = db_client.post("/api/earncash/auth/login", json={"email": "x@example.com"})
    assert resp.status_code == 400


# ======================================
# AUTH PROTECTION
# ======================================
def test_dashboard_requires_token(db_client):
    _register(db_client)
    login_resp = _login(db_client, "test.student@example.com", "testpass123")
    user_id = login_resp.get_json()["user"]["id"]

    resp = db_client.get(f"/api/earncash/users/stats/{user_id}")
    assert resp.status_code == 401
    assert "token is missing" in resp.get_json()["error"]


def test_dashboard_rejects_garbage_token(db_client):
    _register(db_client)
    login_resp = _login(db_client, "test.student@example.com", "testpass123")
    user_id = login_resp.get_json()["user"]["id"]

    resp = db_client.get(
        f"/api/earncash/users/stats/{user_id}",
        headers={"Authorization": "Bearer not-a-real-token"},
    )
    assert resp.status_code == 401
    assert "Invalid authentication token" in resp.get_json()["error"]


def test_user_cannot_access_another_users_profile(db_client):
    _register(db_client, email="user.a@example.com")
    _register(db_client, email="user.b@example.com")

    a_login = _login(db_client, "user.a@example.com", "testpass123")
    b_login = _login(db_client, "user.b@example.com", "testpass123")
    b_user_id = b_login.get_json()["user"]["id"]

    resp = db_client.get(
        f"/api/earncash/users/profile/{b_user_id}",
        headers={"Authorization": f"Bearer {a_login.get_json()['token']}"},
    )
    assert resp.status_code == 403


# ======================================
# DASHBOARD ACCESS (happy path)
# ======================================
def test_dashboard_stats_success(db_client):
    _register(db_client)
    login_resp = _login(db_client, "test.student@example.com", "testpass123")
    token = login_resp.get_json()["token"]
    user_id = login_resp.get_json()["user"]["id"]

    resp = db_client.get(
        f"/api/earncash/users/stats/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["wallet_balance"] == "0.00"
    assert data["total_referrals"] == 0
    assert data["referral_code"]


def test_courses_list_is_public(db_client):
    # /courses has no auth decorator — matches original EarnCash behavior.
    resp = db_client.get("/api/earncash/courses")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_login_malformed_json_body(db_client):
    # Non-JSON body must be handled gracefully (400), never a 500.
    resp = db_client.post(
        "/api/earncash/auth/login",
        data="not json at all",
        content_type="application/json",
    )
    assert resp.status_code == 400


def test_register_malformed_json_body(db_client):
    resp = db_client.post(
        "/api/earncash/auth/register",
        data="{broken json",
        content_type="application/json",
    )
    assert resp.status_code == 400


# ======================================
# helpers for the bigger cross-feature flows below
# ======================================
def _register_and_login(client, email, referral_code=""):
    _register(client, email=email, referral_code=referral_code)
    login = _login(client, email, "testpass123")
    data = login.get_json()
    return data["token"], data["user"]["id"]


def _promote_to_admin(app, user_id):
    """No self-service admin signup exists by design — this mirrors the
    one-time manual promotion an operator performs directly against the
    database the first time an EarnCash admin account is needed."""
    from app.extensions import db
    from app.models import EarnCashUser

    with app.app_context():
        user = db.session.get(EarnCashUser, user_id)
        user.role = "admin"
        db.session.commit()


def _create_course(app, name="Test Course", fee="1000.00"):
    from app.extensions import db
    from app.models import EarnCashCourse

    with app.app_context():
        course = EarnCashCourse(name=name, category="Testing", tuition_fee=fee)
        db.session.add(course)
        db.session.commit()
        return course.id


# ======================================
# COURSES / ENROLLMENT
# ======================================
def test_enroll_requires_auth(db_client, db_app):
    course_id = _create_course(db_app)
    resp = db_client.post("/api/earncash/courses/enroll", json={"course_id": course_id})
    assert resp.status_code == 401


def test_enroll_success_and_my_enrollments(db_client, db_app):
    course_id = _create_course(db_app)
    token, _ = _register_and_login(db_client, "enroll.user@example.com")

    resp = db_client.post(
        "/api/earncash/courses/enroll",
        json={"course_id": course_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    assert resp.get_json()["amount_due"] == "1000.00"

    listing = db_client.get(
        "/api/earncash/courses/my-enrollments",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert listing.status_code == 200
    rows = listing.get_json()
    assert len(rows) == 1
    assert rows[0]["course_name"] == "Test Course"
    assert rows[0]["payment_status"] == "unpaid"


def test_enroll_invalid_course_id(db_client):
    token, _ = _register_and_login(db_client, "badcourse.user@example.com")
    resp = db_client.post(
        "/api/earncash/courses/enroll",
        json={"course_id": 999999},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404


def test_enroll_missing_course_id(db_client):
    token, _ = _register_and_login(db_client, "nocourseid.user@example.com")
    resp = db_client.post(
        "/api/earncash/courses/enroll", json={}, headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 400


# ======================================
# REFERRALS + COMMISSION LOGIC (end-to-end)
# This is the most important business rule in the whole system: a
# commission must only ever be created by an admin verifying a real,
# fully-paid enrollment — never from a signup, never twice.
# ======================================
def test_commission_awarded_only_after_admin_verifies_full_payment(db_client, db_app):
    course_id = _create_course(db_app, fee="1000.00")

    referrer_token, referrer_id = _register_and_login(db_client, "commission.referrer@example.com")
    referrer_code = db_client.get(
        "/api/earncash/referrals/code", headers={"Authorization": f"Bearer {referrer_token}"}
    ).get_json()["referral_code"]

    student_token, student_id = _register_and_login(
        db_client, "commission.student@example.com", referral_code=referrer_code
    )

    enroll_resp = db_client.post(
        "/api/earncash/courses/enroll",
        json={"course_id": course_id},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    enrollment_id = enroll_resp.get_json()["enrollment_id"]

    admin_token, admin_id = _register_and_login(db_client, "commission.admin@example.com")
    _promote_to_admin(db_app, admin_id)
    # re-login to get a token carrying role=admin (role is baked into the JWT at issue time)
    admin_token = _login(db_client, "commission.admin@example.com", "testpass123").get_json()["token"]

    # Partial payment must NOT award a commission yet.
    partial_resp = db_client.put(
        f"/api/earncash/admin/enrollments/{enrollment_id}/verify-payment",
        json={"amount_paid": 400},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert partial_resp.status_code == 200
    assert partial_resp.get_json()["payment_status"] == "partial"
    assert partial_resp.get_json()["commission_created"] is False

    # Completing the payment (400 + 600 = 1000 = amount_due) must award
    # exactly one commission, at the configured rate (default 10%).
    final_resp = db_client.put(
        f"/api/earncash/admin/enrollments/{enrollment_id}/verify-payment",
        json={"amount_paid": 600},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert final_resp.status_code == 200
    body = final_resp.get_json()
    assert body["payment_status"] == "paid"
    assert body["commission_created"] is True
    assert body["commission_amount"] == "100.0"  # 10% of 1000.00

    # The referrer's wallet must now reflect the commission.
    stats_resp = db_client.get(
        f"/api/earncash/users/stats/{referrer_id}",
        headers={"Authorization": f"Bearer {referrer_token}"},
    )
    assert stats_resp.get_json()["wallet_balance"] == "100.00"
    assert stats_resp.get_json()["total_commission_earned"] == "100.00"

    # Referrer's commission listing must show exactly one row, correctly
    # attributed to the referred student and the course.
    commissions_resp = db_client.get(
        f"/api/earncash/referrals/{referrer_id}/commissions",
        headers={"Authorization": f"Bearer {referrer_token}"},
    )
    rows = commissions_resp.get_json()
    assert len(rows) == 1
    assert rows[0]["referred_user_name"] == "Test Student"
    assert rows[0]["course_name"] == "Test Course"

    # Verifying payment again on the same (already-paid) enrollment must
    # NOT award a second commission.
    repeat_resp = db_client.put(
        f"/api/earncash/admin/enrollments/{enrollment_id}/verify-payment",
        json={"amount_paid": 50},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert repeat_resp.status_code == 200
    assert repeat_resp.get_json()["commission_created"] is False

    stats_after_repeat = db_client.get(
        f"/api/earncash/users/stats/{referrer_id}",
        headers={"Authorization": f"Bearer {referrer_token}"},
    )
    assert stats_after_repeat.get_json()["wallet_balance"] == "100.00"  # unchanged


def test_referral_listing_shows_referred_user(db_client):
    referrer_token, referrer_id = _register_and_login(db_client, "reflist.referrer@example.com")
    code = db_client.get(
        "/api/earncash/referrals/code", headers={"Authorization": f"Bearer {referrer_token}"}
    ).get_json()["referral_code"]
    _register(db_client, email="reflist.referred@example.com", fullname="Referred Person", referral_code=code)

    resp = db_client.get(
        f"/api/earncash/referrals/{referrer_id}",
        headers={"Authorization": f"Bearer {referrer_token}"},
    )
    assert resp.status_code == 200
    rows = resp.get_json()
    assert len(rows) == 1
    assert rows[0]["fullname"] == "Referred Person"


# ======================================
# WITHDRAWALS
# ======================================
def test_withdrawal_insufficient_balance(db_client):
    token, _ = _register_and_login(db_client, "withdraw.poor@example.com")
    resp = db_client.post(
        "/api/earncash/withdrawals/request",
        json={"amount": 1000, "method": "mpesa", "details": "0712345678"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400
    assert "Insufficient wallet balance" in resp.get_json()["error"]


def test_withdrawal_below_minimum_amount(db_client):
    token, _ = _register_and_login(db_client, "withdraw.small@example.com")
    resp = db_client.post(
        "/api/earncash/withdrawals/request",
        json={"amount": 10, "method": "mpesa", "details": "0712345678"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400
    assert "Minimum withdrawal" in resp.get_json()["error"]


def test_withdrawal_zero_amount(db_client):
    token, _ = _register_and_login(db_client, "withdraw.zero@example.com")
    resp = db_client.post(
        "/api/earncash/withdrawals/request",
        json={"amount": 0, "method": "mpesa", "details": "0712345678"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400


def test_withdrawal_negative_amount(db_client):
    token, _ = _register_and_login(db_client, "withdraw.negative@example.com")
    resp = db_client.post(
        "/api/earncash/withdrawals/request",
        json={"amount": -500, "method": "mpesa", "details": "0712345678"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400


def test_withdrawal_invalid_method(db_client):
    token, _ = _register_and_login(db_client, "withdraw.badmethod@example.com")
    resp = db_client.post(
        "/api/earncash/withdrawals/request",
        json={"amount": 1000, "method": "paypal", "details": "x"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400
    assert "must be one of" in resp.get_json()["error"]


def test_withdrawal_full_flow_request_approve(db_client, db_app):
    # Build up a wallet balance via a verified commission first.
    course_id = _create_course(db_app, fee="5000.00")
    referrer_token, referrer_id = _register_and_login(db_client, "wflow.referrer@example.com")
    code = db_client.get(
        "/api/earncash/referrals/code", headers={"Authorization": f"Bearer {referrer_token}"}
    ).get_json()["referral_code"]
    student_token, _ = _register_and_login(db_client, "wflow.student@example.com", referral_code=code)
    enrollment_id = db_client.post(
        "/api/earncash/courses/enroll", json={"course_id": course_id},
        headers={"Authorization": f"Bearer {student_token}"},
    ).get_json()["enrollment_id"]

    admin_token, admin_id = _register_and_login(db_client, "wflow.admin@example.com")
    _promote_to_admin(db_app, admin_id)
    admin_token = _login(db_client, "wflow.admin@example.com", "testpass123").get_json()["token"]
    db_client.put(
        f"/api/earncash/admin/enrollments/{enrollment_id}/verify-payment",
        json={"amount_paid": 5000},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    # Referrer now has a 500 KES commission (10% of 5000) — above the
    # KES 500 minimum withdrawal.
    withdraw_resp = db_client.post(
        "/api/earncash/withdrawals/request",
        json={"amount": 500, "method": "mpesa", "details": "0712345678"},
        headers={"Authorization": f"Bearer {referrer_token}"},
    )
    assert withdraw_resp.status_code == 201
    withdrawal_id = withdraw_resp.get_json()["withdrawal_id"]

    # Wallet must be debited (reserved) immediately.
    stats_after_request = db_client.get(
        f"/api/earncash/users/stats/{referrer_id}",
        headers={"Authorization": f"Bearer {referrer_token}"},
    )
    assert stats_after_request.get_json()["wallet_balance"] == "0.00"

    # History must show it as pending.
    history_resp = db_client.get(
        f"/api/earncash/withdrawals/history/{referrer_id}",
        headers={"Authorization": f"Bearer {referrer_token}"},
    )
    assert history_resp.get_json()[0]["status"] == "pending"

    # Admin approves.
    approve_resp = db_client.put(
        f"/api/earncash/admin/withdrawals/{withdrawal_id}/approve",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert approve_resp.status_code == 200

    history_after = db_client.get(
        f"/api/earncash/withdrawals/history/{referrer_id}",
        headers={"Authorization": f"Bearer {referrer_token}"},
    )
    assert history_after.get_json()[0]["status"] == "approved"


def test_withdrawal_rejection_refunds_wallet(db_client, db_app):
    course_id = _create_course(db_app, fee="5000.00")
    referrer_token, referrer_id = _register_and_login(db_client, "wreject.referrer@example.com")
    code = db_client.get(
        "/api/earncash/referrals/code", headers={"Authorization": f"Bearer {referrer_token}"}
    ).get_json()["referral_code"]
    student_token, _ = _register_and_login(db_client, "wreject.student@example.com", referral_code=code)
    enrollment_id = db_client.post(
        "/api/earncash/courses/enroll", json={"course_id": course_id},
        headers={"Authorization": f"Bearer {student_token}"},
    ).get_json()["enrollment_id"]

    admin_token, admin_id = _register_and_login(db_client, "wreject.admin@example.com")
    _promote_to_admin(db_app, admin_id)
    admin_token = _login(db_client, "wreject.admin@example.com", "testpass123").get_json()["token"]
    db_client.put(
        f"/api/earncash/admin/enrollments/{enrollment_id}/verify-payment",
        json={"amount_paid": 5000},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    withdrawal_id = db_client.post(
        "/api/earncash/withdrawals/request",
        json={"amount": 500, "method": "bank", "details": "acct-123"},
        headers={"Authorization": f"Bearer {referrer_token}"},
    ).get_json()["withdrawal_id"]

    reject_resp = db_client.put(
        f"/api/earncash/admin/withdrawals/{withdrawal_id}/reject",
        json={"reason": "Test rejection"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert reject_resp.status_code == 200

    # Funds must be returned to the wallet.
    stats_resp = db_client.get(
        f"/api/earncash/users/stats/{referrer_id}",
        headers={"Authorization": f"Bearer {referrer_token}"},
    )
    assert stats_resp.get_json()["wallet_balance"] == "500.00"


# ======================================
# NOTIFICATIONS
# ======================================
def test_notifications_created_by_withdrawal_flow_and_isolated_per_user(db_client, db_app):
    course_id = _create_course(db_app, fee="5000.00")
    referrer_token, referrer_id = _register_and_login(db_client, "notif.referrer@example.com")
    other_token, _ = _register_and_login(db_client, "notif.other@example.com")

    code = db_client.get(
        "/api/earncash/referrals/code", headers={"Authorization": f"Bearer {referrer_token}"}
    ).get_json()["referral_code"]
    student_token, _ = _register_and_login(db_client, "notif.student@example.com", referral_code=code)
    enrollment_id = db_client.post(
        "/api/earncash/courses/enroll", json={"course_id": course_id},
        headers={"Authorization": f"Bearer {student_token}"},
    ).get_json()["enrollment_id"]

    admin_token, admin_id = _register_and_login(db_client, "notif.admin@example.com")
    _promote_to_admin(db_app, admin_id)
    admin_token = _login(db_client, "notif.admin@example.com", "testpass123").get_json()["token"]
    db_client.put(
        f"/api/earncash/admin/enrollments/{enrollment_id}/verify-payment",
        json={"amount_paid": 5000},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # Verifying payment creates a "Commission received" notification for
    # the referrer.
    own_notifs = db_client.get(
        f"/api/earncash/notifications/{referrer_id}",
        headers={"Authorization": f"Bearer {referrer_token}"},
    ).get_json()
    assert any(n["title"] == "Commission received" for n in own_notifs)
    assert all(n["status"] == "unread" for n in own_notifs)

    # Another user must not be able to read the referrer's notifications.
    cross_access = db_client.get(
        f"/api/earncash/notifications/{referrer_id}",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert cross_access.status_code == 403

    # Mark as read.
    notif_id = own_notifs[0]["id"]
    mark_resp = db_client.put(
        f"/api/earncash/notifications/read/{notif_id}",
        headers={"Authorization": f"Bearer {referrer_token}"},
    )
    assert mark_resp.status_code == 200

    # Another user must not be able to mark/delete someone else's notification.
    other_mark = db_client.put(
        f"/api/earncash/notifications/read/{notif_id}",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert other_mark.status_code == 403

    delete_resp = db_client.delete(
        f"/api/earncash/notifications/delete/{notif_id}",
        headers={"Authorization": f"Bearer {referrer_token}"},
    )
    assert delete_resp.status_code == 200


# ======================================
# ADMIN AUTH + AUTHORIZATION
# ======================================
def test_admin_login_rejects_non_admin_account(db_client):
    _register(db_client, email="notadmin@example.com")
    resp = db_client.post(
        "/api/earncash/admin/login",
        json={"email": "notadmin@example.com", "password": "testpass123"},
    )
    assert resp.status_code == 401
    assert "Invalid admin credentials" in resp.get_json()["error"]


def test_admin_login_success_after_promotion(db_client, db_app):
    _, user_id = _register_and_login(db_client, "realadmin@example.com")
    _promote_to_admin(db_app, user_id)

    resp = db_client.post(
        "/api/earncash/admin/login",
        json={"email": "realadmin@example.com", "password": "testpass123"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["token"]
    assert data["admin"]["role"] == "admin"


def test_regular_user_token_rejected_from_admin_endpoints(db_client):
    token, _ = _register_and_login(db_client, "plainuser@example.com")
    resp = db_client.get("/api/earncash/admin/stats", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403
    assert "Admin privileges required" in resp.get_json()["error"]


def test_admin_endpoints_reject_missing_token(db_client):
    resp = db_client.get("/api/earncash/admin/users")
    assert resp.status_code == 401


def test_admin_stats_and_users_list(db_client, db_app):
    _register_and_login(db_client, "statsuser1@example.com")
    _register_and_login(db_client, "statsuser2@example.com")
    _, admin_id = _register_and_login(db_client, "statsadmin@example.com")
    _promote_to_admin(db_app, admin_id)
    admin_token = _login(db_client, "statsadmin@example.com", "testpass123").get_json()["token"]

    stats_resp = db_client.get("/api/earncash/admin/stats", headers={"Authorization": f"Bearer {admin_token}"})
    assert stats_resp.status_code == 200
    body = stats_resp.get_json()
    assert body["total_users"] >= 2  # excludes the admin itself (role='user' filter)

    users_resp = db_client.get("/api/earncash/admin/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert users_resp.status_code == 200
    emails = [u["email"] for u in users_resp.get_json()]
    assert "statsadmin@example.com" not in emails  # admin excluded from the user list


def test_admin_can_create_course(db_client, db_app):
    _, admin_id = _register_and_login(db_client, "courseadmin@example.com")
    _promote_to_admin(db_app, admin_id)
    admin_token = _login(db_client, "courseadmin@example.com", "testpass123").get_json()["token"]

    resp = db_client.post(
        "/api/earncash/admin/courses",
        json={"name": "New Course", "category": "Testing", "tuition_fee": 2500},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 201
    assert resp.get_json()["course_id"]

    public_list = db_client.get("/api/earncash/courses").get_json()
    assert any(c["name"] == "New Course" for c in public_list)


def test_admin_enrollments_listing(db_client, db_app):
    course_id = _create_course(db_app, fee="1000.00")
    student_token, _ = _register_and_login(db_client, "adminlist.student@example.com")
    db_client.post(
        "/api/earncash/courses/enroll", json={"course_id": course_id},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    _, admin_id = _register_and_login(db_client, "adminlist.admin@example.com")
    _promote_to_admin(db_app, admin_id)
    admin_token = _login(db_client, "adminlist.admin@example.com", "testpass123").get_json()["token"]

    resp = db_client.get(
        "/api/earncash/admin/enrollments?status=unpaid",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    assert any(e["student_name"] == "Test Student" for e in resp.get_json())


# ======================================
# EARNCASH ADMIN JWT MUST NEVER SUBSTITUTE FOR GERMAINE'S SESSION ADMIN AUTH
# ======================================
def test_earncash_admin_jwt_does_not_grant_access_to_germaine_admin_portal(db_client, db_app):
    _, admin_id = _register_and_login(db_client, "crosscheck.admin@example.com")
    _promote_to_admin(db_app, admin_id)
    admin_token = _login(db_client, "crosscheck.admin@example.com", "testpass123").get_json()["token"]

    # Germaine's staff admin portal is session-cookie authenticated and
    # lives outside /api/ entirely — an EarnCash bearer token must have
    # no effect on it whatsoever.
    resp = db_client.get(
        "/admin/dashboard",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    # Whatever Germaine's own auth guard does for an unauthenticated
    # session (redirect to login, or 401/403) — it must NOT be 200.
    assert resp.status_code != 200
