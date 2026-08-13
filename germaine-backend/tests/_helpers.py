"""Shared test data builders (not a test file itself — no test_ prefix)."""

import re

from app.extensions import db
from app.models import (
    School, Department, ProgrammeCategory, Programme, ProgrammeMode, ProgrammeFAQ,
    ProgrammeFeature, AdminUser, EarnCashUser,
)
from app.utils.security import hash_password


def seed_minimal_catalogue():
    """Creates one school (with one department), one academic programme
    under that department, one programme category, and one AI Bootcamp
    programme with a mode/faq/feature. Returns a dict of the created rows."""
    school = School(slug="health", name="School of Health Sciences", fee="KES 11,500",
                     is_active=True, display_order=0)
    db.session.add(school)
    db.session.flush()

    department = Department(school_id=school.id, name="Nursing")
    db.session.add(department)
    db.session.flush()

    academic = Programme(
        programme_type="academic", slug="diploma-in-nursing", school_id=school.id,
        department_id=department.id, name="Diploma in Nursing", level="Diploma",
        level_class="diploma", duration="2 Years", entry_requirement="KCSE C- & above", exam_body="KNEC",
        is_active=True,
    )
    db.session.add(academic)

    category = ProgrammeCategory(slug="ai", label="Artificial Intelligence", icon="fa-brain")
    db.session.add(category)
    db.session.flush()

    ai_programme = Programme(
        programme_type="ai_bootcamp", slug="ai-ml", category_id=category.id,
        name="Artificial Intelligence & Machine Learning", level="Intermediate",
        duration="16 Weeks", overview="Learn AI.", gain_points=["Build ML models"],
        is_active=True,
    )
    db.session.add(ai_programme)
    db.session.flush()

    mode = ProgrammeMode(
        programme_id=ai_programme.id, mode_key="ft-hybrid", label="Full-time",
        sub_label="Hybrid", duration="16 Weeks", start_date=None, fee_amount=145000,
        fee_currency="KES", schedule="Mon-Fri", is_available=True,
    )
    db.session.add(mode)

    faq = ProgrammeFAQ(programme_id=ai_programme.id, question="Fees?", answer="See pricing.")
    db.session.add(faq)

    feature = ProgrammeFeature(programme_id=ai_programme.id, title="Mentor Support", description="1:1 mentorship")
    db.session.add(feature)

    db.session.commit()
    return {
        "school": school, "department": department, "academic": academic,
        "category": category, "ai_programme": ai_programme, "mode": mode,
    }


def create_admin_user(email="admin@example.com", password="Sup3rSecret!1", name="Test Admin", is_active=True):
    admin = AdminUser(name=name, email=email, password_hash=hash_password(password), is_active=is_active)
    db.session.add(admin)
    db.session.commit()
    return admin


def create_earncash_user(fullname="Referrer One", email="referrer@example.com",
                          referral_code="ECREFCODE1", wallet=0):
    user = EarnCashUser(
        fullname=fullname, email=email, password_hash=hash_password("Sup3rSecret!1"),
        referral_code=referral_code, wallet=wallet,
    )
    db.session.add(user)
    db.session.commit()
    return user


CSRF_RE = re.compile(rb'name="csrf_token" value="([^"]+)"')


def get_csrf_from(response):
    match = CSRF_RE.search(response.data)
    assert match, "No CSRF token found in response body."
    return match.group(1).decode()


def login_admin(client, email="admin@example.com", password="Sup3rSecret!1"):
    """Logs the given client in via the real /admin/login form flow (fetches a
    real CSRF token first, exactly as a browser would) and returns the response."""
    get_resp = client.get("/admin/login")
    token = get_csrf_from(get_resp)
    return client.post(
        "/admin/login",
        data={"email": email, "password": password, "csrf_token": token},
        follow_redirects=False,
    )
