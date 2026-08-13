"""
Scholarship information service (Step 5).

Step 2 §10 established there is no separate `scholarships` table:
`apply.html`'s own heading is literally "Apply for a Full Scholarship,"
and `application_type` defaults to `'scholarship'` on every application
row. This module does not invent eligibility rules, award amounts, or
financial conditions that were never approved anywhere in Steps 2-4 —
it only describes the real, already-designed workflow and required
fields, so a frontend can render an accurate "how to apply" summary.
"""

from app.services.application_service import ALLOWED_APPLICATION_TYPES


def get_scholarship_info() -> dict:
    return {
        "application_type": "scholarship",
        "description": (
            "The scholarship application is Germaine's single application flow "
            "(application_type='scholarship' by default) — there is no separate "
            "scholarship program, award tier, or eligibility table in this system. "
            "Submitting POST /api/admissions/applications with no application_type "
            "specified creates a scholarship application."
        ),
        "required_fields": [
            "full_name", "email", "phone", "programme_id", "consent",
        ],
        "optional_fields": [
            "national_id", "date_of_birth", "gender", "county",
            "education_level", "kcse_grade", "programme_mode_id (AI Bootcamp programmes only)",
        ],
        "other_application_types": sorted(ALLOWED_APPLICATION_TYPES - {"scholarship"}),
        "note": (
            "No award amounts, financial conditions, or eligibility rules are "
            "defined here — none were specified in the approved Step 2 "
            "architecture, and none are invented by this service."
        ),
    }
