"""
ApplicantLead — real-time applicant lead capture (additive, new table).

A lead is a prospective applicant who has typed a valid name and Kenyan
phone number into the public application form (build10/apply.html), whether
or not they ever press Submit. It is deliberately a SEPARATE table from
`applicants`/`applications`:

  - `applications` stays the record of officially submitted applications.
    A lead is never treated as a submitted application merely because
    someone started typing; only a successful POST /api/admissions/applications
    links a lead to an application (application_id + lead_status
    'application_submitted').

  - Identity: each browser gets a random, client-generated lead token
    (kept in that browser's localStorage). Only its SHA-256 hash is stored
    here (`lead_token_hash`, UNIQUE). The same token always updates the same
    row, so keystrokes, retries, phone corrections and return visits from
    the same browser never create duplicates. Two different browsers that
    happen to type the same phone number are NOT silently merged — identity
    cannot be verified that way — the admin dashboard shows them as
    "possible duplicates" (same normalized_phone) instead.

  - application_id uses ON DELETE SET NULL: deleting an application never
    deletes a lead, and (because the FK lives on this table) deleting a
    lead can never delete an application, applicant, document, payment or
    any other admissions record. No cascade is configured in either direction.
"""

from datetime import datetime, timezone

from app.extensions import db

LEAD_STATUSES = [
    "new_lead",
    "contacted",
    "interested",
    "follow_up_required",
    "application_submitted",
    "not_interested",
]

LEAD_STATUS_LABELS = {
    "new_lead": "New Lead",
    "contacted": "Contacted",
    "interested": "Interested",
    "follow_up_required": "Follow-up Required",
    "application_submitted": "Application Submitted",
    "not_interested": "Not Interested",
}


def _now():
    return datetime.now(timezone.utc)


class ApplicantLead(db.Model):
    __tablename__ = "applicant_leads"
    __table_args__ = (
        db.CheckConstraint(
            "lead_status IN ('new_lead', 'contacted', 'interested', 'follow_up_required', "
            "'application_submitted', 'not_interested')",
            name="ck_applicant_leads_lead_status",
        ),
        db.UniqueConstraint("lead_token_hash", name="uq_applicant_leads_lead_token_hash"),
        db.Index("ix_applicant_leads_normalized_phone", "normalized_phone"),
        db.Index("ix_applicant_leads_lead_status", "lead_status"),
        db.Index("ix_applicant_leads_first_captured_at", "first_captured_at"),
        db.Index("ix_applicant_leads_application_id", "application_id"),
    )

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)

    # SHA-256 hex of the browser's anonymous lead token — never the raw token.
    lead_token_hash = db.Column(db.String(64), nullable=False)

    applicant_name = db.Column(db.String(200), nullable=False)
    phone_number = db.Column(db.String(30), nullable=False)       # as typed (trimmed)
    normalized_phone = db.Column(db.String(12), nullable=False)   # 2547XXXXXXXX / 2541XXXXXXXX
    email = db.Column(db.String(200), nullable=True)
    programme = db.Column(db.String(255), nullable=True)          # display name from the form
    school = db.Column(db.String(120), nullable=True)
    application_type = db.Column(db.String(30), nullable=False, default="scholarship")
    source_page = db.Column(db.String(120), nullable=True)

    lead_status = db.Column(db.String(30), nullable=False, default="new_lead")
    application_id = db.Column(
        db.BigInteger, db.ForeignKey("applications.id", ondelete="SET NULL"), nullable=True
    )

    first_captured_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_now)
    last_updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_now)   # applicant-side data change
    last_activity_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_now)  # any applicant activity
    contacted_at = db.Column(db.DateTime(timezone=True), nullable=True)
    follow_up_notes = db.Column(db.Text, nullable=True)
    anonymized_at = db.Column(db.DateTime(timezone=True), nullable=True)

    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_now)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_now, onupdate=_now)

    # passive_deletes + no cascade: this relationship can never delete an Application.
    application = db.relationship("Application", foreign_keys=[application_id], passive_deletes=True)

    @property
    def status_label(self):
        return LEAD_STATUS_LABELS.get(self.lead_status, self.lead_status)

    @property
    def application_status(self):
        return "Submitted" if self.application_id else "Incomplete"

    def __repr__(self):
        return f"<ApplicantLead id={self.id} status={self.lead_status!r}>"


class ApplicantLeadAuditLog(db.Model):
    """Append-only record of sensitive admin actions on leads (status/notes
    changes, anonymisation, deletion). Deliberately stores NO applicant name,
    phone or email — only the lead id, a masked phone suffix and the acting
    admin — so a deleted lead's personal data is not retained here."""

    __tablename__ = "applicant_lead_audit_logs"

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    lead_id = db.Column(db.BigInteger, nullable=False, index=True)  # no FK: survives lead deletion
    admin_user_id = db.Column(
        db.BigInteger, db.ForeignKey("admin_users.id", ondelete="SET NULL"), nullable=True
    )
    action = db.Column(db.String(40), nullable=False)
    detail = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_now)

    admin_user = db.relationship("AdminUser", foreign_keys=[admin_user_id])
