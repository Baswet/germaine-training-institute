"""
Model registry.

Importing this package registers all 28 SQLAlchemy models against the
shared `db` metadata (app/extensions.py). This module deliberately
contains no query logic, no db.create_all(), and is never used to
connect to or modify a live database — it only wires model classes to
metadata so Alembic can later autogenerate migrations against them.

15 of these models match Step 2 (STEP-2-DATABASE-ARCHITECTURE.md) §28
exactly, unchanged since Step 4. 4 more (MediaAsset, NewsArticle,
SiteContent, ContentListItem) are the Step 7 CMS addition — each is
documented as a "CMS SCHEMA CHANGE REQUIRED" in its own model file,
explaining exactly why the approved Step 2 schema could not represent
it and what was added. No other speculative model (Vacancy, Employer,
Graduate directory, ApplicationDocument, AuditLog, Role, Permission)
is included — see STEP-2-DATABASE-ARCHITECTURE.md §35 for what remains
deliberately deferred and why.

The remaining 8 (EarnCashUser, EarnCashCourse, EarnCashEnrollment,
EarnCashReferralCommission, EarnCashTransaction, EarnCashWithdrawal,
EarnCashNotification, EarnCashAdminLog) are the EarnCash integration:
A 28th model, EarnCashApplicationCommission, was added afterward to
bridge EarnFastCash referrals to real GTI `applications` (see its own
file for why it is a separate table from EarnCashReferralCommission).
EarnCash was originally a fully separate Flask+MySQL application
(build10/EarnCash/backend/) that could not reach its own backend
because it was never set up and collided with this app's port. Rather
than stand up a second server and a second database engine, its 8
tables were ported here 1:1 (see each earncash_*.py file's docstring
for the MySQL -> PostgreSQL conversion notes) as `earncash_`-prefixed
tables — additive only, no existing table touched or renamed.

ApplicantLead + ApplicantLeadAuditLog (additive) back the real-time
applicant lead capture feature — see app/models/applicant_lead.py.
"""

from app.models.school import School
from app.models.department import Department
from app.models.programme_category import ProgrammeCategory
from app.models.programme import Programme
from app.models.programme_mode import ProgrammeMode
from app.models.programme_faq import ProgrammeFAQ
from app.models.programme_feature import ProgrammeFeature
from app.models.applicant import Applicant
from app.models.application import Application
from app.models.alumni import Alumni
from app.models.graduate_profile_request import GraduateProfileRequest
from app.models.partner_enquiry import PartnerEnquiry
from app.models.contact_message import ContactMessage
from app.models.newsletter_subscriber import NewsletterSubscriber
from app.models.admin_user import AdminUser
from app.models.media_asset import MediaAsset
from app.models.news_article import NewsArticle
from app.models.site_content import SiteContent
from app.models.content_list_item import ContentListItem
from app.models.earncash_user import EarnCashUser
from app.models.earncash_course import EarnCashCourse
from app.models.earncash_enrollment import EarnCashEnrollment
from app.models.earncash_referral_commission import EarnCashReferralCommission
from app.models.earncash_transaction import EarnCashTransaction
from app.models.earncash_withdrawal import EarnCashWithdrawal
from app.models.earncash_notification import EarnCashNotification
from app.models.earncash_admin_log import EarnCashAdminLog
from app.models.earncash_application_commission import EarnCashApplicationCommission
from app.models.applicant_lead import ApplicantLead, ApplicantLeadAuditLog
from app.models.newsroom import NewsArticleMeta, NewsEvent

__all__ = [
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
    "MediaAsset",
    "NewsArticle",
    "SiteContent",
    "ContentListItem",
    "EarnCashUser",
    "EarnCashCourse",
    "EarnCashEnrollment",
    "EarnCashReferralCommission",
    "EarnCashTransaction",
    "EarnCashWithdrawal",
    "EarnCashNotification",
    "EarnCashAdminLog",
    "EarnCashApplicationCommission",
    "ApplicantLead",
    "ApplicantLeadAuditLog",
    "NewsArticleMeta",
    "NewsEvent",
]
