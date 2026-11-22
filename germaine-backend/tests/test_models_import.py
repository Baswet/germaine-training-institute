"""
Verifies all models import cleanly with no circular imports.

This test imports models only; it never calls db.create_all(), opens a
connection, or issues a query.

STEP_2_MODELS is the original, approved 15-table baseline
(STEP-2-DATABASE-ARCHITECTURE.md §28) and must never change size or
membership without an explicit, documented Step 2 revision.

CMS_MODELS is the Step 7 CMS addition (4 models: MediaAsset,
NewsArticle, SiteContent, ContentListItem) — each documented as a "CMS
SCHEMA CHANGE REQUIRED" in its own model file. The combined registry is
therefore 19, not 15 — this is an intentional, documented growth, not a
regression of the "exactly 15" guarantee that predates the CMS.

EARNCASH_MODELS is the EarnCash integration (9 models, all
`earncash_`-prefixed tables): EarnCash was originally a fully separate
Flask+MySQL application that could not reach its own never-configured
backend. Rather than stand up a second server/database, its schema was
ported here 1:1 as additive-only tables — see app/models/earncash_*.py
and app/models/__init__.py for the full rationale. The 9th model,
EarnCashApplicationCommission, is the additive GTI-application referral
bridge added later (see app/models/earncash_application_commission.py).
The combined registry was therefore 28; the 2 applicant-lead models
(LEAD_MODELS below) bring it to 30.
"""

from app import models


STEP_2_MODELS = {
    "School",
    "Department",
    "ProgrammeCategory",
    "Programme",
    "ProgrammeMode",
    "ProgrammeFAQ",
    "ProgrammeFeature",
    "Applicant",
    "Application",
    "Alumni",
    "GraduateProfileRequest",
    "PartnerEnquiry",
    "ContactMessage",
    "NewsletterSubscriber",
    "AdminUser",
}

CMS_MODELS = {
    "MediaAsset",
    "NewsArticle",
    "SiteContent",
    "ContentListItem",
}

EARNCASH_MODELS = {
    "EarnCashUser",
    "EarnCashCourse",
    "EarnCashEnrollment",
    "EarnCashReferralCommission",
    "EarnCashTransaction",
    "EarnCashWithdrawal",
    "EarnCashNotification",
    "EarnCashAdminLog",
    "EarnCashApplicationCommission",
}

# Applicant lead capture (additive): leads + a lead-scoped admin audit log.
# ApplicantLeadAuditLog is deliberately scoped to leads only — the generic,
# speculative "AuditLog" below stays forbidden.
LEAD_MODELS = {
    "ApplicantLead",
    "ApplicantLeadAuditLog",
}

# News & Events publication (additive): 1:1 article extension + events.
NEWSROOM_MODELS = {
    "NewsArticleMeta",
    "NewsEvent",
}

EXPECTED_MODELS = STEP_2_MODELS | CMS_MODELS | EARNCASH_MODELS | LEAD_MODELS | NEWSROOM_MODELS

# Explicitly forbidden speculative models (Step 2 §35 / Step 3 instructions).
# "News" (bare) stays forbidden — the real model is "NewsArticle", added
# deliberately in Step 7 with its own documented schema-change rationale,
# not a bare speculative "News" table.
FORBIDDEN_MODEL_NAMES = {
    "News",
    "Vacancy",
    "Employer",
    "Graduate",
    "ApplicationDocument",
    "AuditLog",
    "Role",
    "Permission",
}


def test_step2_baseline_models_unchanged():
    """The original approved 15 remain exactly intact — Step 7's CMS
    addition must be purely additive, never a modification of these."""
    assert STEP_2_MODELS.issubset(set(models.__all__))
    assert len(STEP_2_MODELS) == 15


def test_all_models_exported_match_registry():
    assert set(models.__all__) == EXPECTED_MODELS
    assert len(models.__all__) == 32


def test_earncash_models_use_prefixed_tablenames():
    """Every EarnCash table is `earncash_`-prefixed so it can never
    collide with an existing or future Germaine table name."""
    for model_name in EARNCASH_MODELS:
        model_class = getattr(models, model_name)
        assert model_class.__tablename__.startswith("earncash_")


def test_no_forbidden_speculative_models_defined():
    exported = set(models.__all__)
    assert exported.isdisjoint(FORBIDDEN_MODEL_NAMES)


def test_each_model_has_expected_tablename():
    expected_tablenames = {
        "School": "schools",
        "Department": "departments",
        "ProgrammeCategory": "programme_categories",
        "Programme": "programmes",
        "ProgrammeMode": "programme_modes",
        "ProgrammeFAQ": "programme_faqs",
        "ProgrammeFeature": "programme_features",
        "Applicant": "applicants",
        "Application": "applications",
        "Alumni": "alumni",
        "GraduateProfileRequest": "graduate_profile_requests",
        "PartnerEnquiry": "partner_enquiries",
        "ContactMessage": "contact_messages",
        "NewsletterSubscriber": "newsletter_subscribers",
        "AdminUser": "admin_users",
    }
    for model_name, expected_table in expected_tablenames.items():
        model_class = getattr(models, model_name)
        assert model_class.__tablename__ == expected_table


def test_programme_fee_not_present_academic_pricing_kept_on_school():
    # Step 2 §8: academic fee lives on School.fee, never Programme.fee.
    assert hasattr(models.School, "fee")
    assert not hasattr(models.Programme, "fee")


def test_programme_mode_fee_and_start_date_are_nullable():
    # Step 2 §8: NULL is the "Contact Admissions" / "Applications Open"
    # sentinel — never a stored literal string.
    fee_col = models.ProgrammeMode.__table__.columns["fee_amount"]
    start_date_col = models.ProgrammeMode.__table__.columns["start_date"]
    assert fee_col.nullable is True
    assert start_date_col.nullable is True


def test_application_reference_code_is_unique_and_separate_from_id():
    ref_col = models.Application.__table__.columns["reference_code"]
    assert ref_col.unique is True
    assert ref_col.name != "id"


def test_admin_user_has_no_role_or_permissions_column():
    # Step 3 instructions: no role/permissions field yet on AdminUser.
    assert not hasattr(models.AdminUser, "role")
    assert not hasattr(models.AdminUser, "permissions")
