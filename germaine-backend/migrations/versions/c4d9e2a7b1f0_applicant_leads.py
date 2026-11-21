"""Applicant leads: real-time lead capture + lead audit log (additive only)

Revision ID: c4d9e2a7b1f0
Revises: 8b1f4c9d2e3a
Create Date: 2026-11-21

ADDITIVE ONLY. Creates two new tables and their indexes; touches no
existing table, column, index or row.

Hand-written on purpose: `flask db migrate` against this schema also
proposes dropping nine pre-existing indexes (ix_applications_referred_by_
earncash_user_id and eight ix_earncash_* indexes) because those indexes
exist in earlier migrations but are not declared on the models. Dropping
them would be an unrelated, destructive change, so they are deliberately
NOT included here.

Deletion safety: applicant_leads.application_id -> applications.id is
ON DELETE SET NULL. The FK lives on the lead table, so deleting a lead
can never delete an application (or applicant, document or payment), and
deleting an application only unlinks the lead. applicant_lead_audit_logs
has no FK to applicant_leads, so audit entries survive lead deletion.

Downgrade drops ONLY these two new tables (and therefore any lead data in
them); it never touches pre-existing tables.
"""
from alembic import op
import sqlalchemy as sa


revision = 'c4d9e2a7b1f0'
down_revision = '8b1f4c9d2e3a'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'applicant_leads',
        sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False),
        sa.Column('lead_token_hash', sa.String(length=64), nullable=False),
        sa.Column('applicant_name', sa.String(length=200), nullable=False),
        sa.Column('phone_number', sa.String(length=30), nullable=False),
        sa.Column('normalized_phone', sa.String(length=12), nullable=False),
        sa.Column('email', sa.String(length=200), nullable=True),
        sa.Column('programme', sa.String(length=255), nullable=True),
        sa.Column('school', sa.String(length=120), nullable=True),
        sa.Column('application_type', sa.String(length=30), nullable=False),
        sa.Column('source_page', sa.String(length=120), nullable=True),
        sa.Column('lead_status', sa.String(length=30), nullable=False),
        sa.Column('application_id', sa.BigInteger(), nullable=True),
        sa.Column('first_captured_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_activity_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('contacted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('follow_up_notes', sa.Text(), nullable=True),
        sa.Column('anonymized_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "lead_status IN ('new_lead', 'contacted', 'interested', 'follow_up_required', "
            "'application_submitted', 'not_interested')",
            name='ck_applicant_leads_lead_status',
        ),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('lead_token_hash', name='uq_applicant_leads_lead_token_hash'),
    )
    op.create_index('ix_applicant_leads_normalized_phone', 'applicant_leads', ['normalized_phone'])
    op.create_index('ix_applicant_leads_lead_status', 'applicant_leads', ['lead_status'])
    op.create_index('ix_applicant_leads_first_captured_at', 'applicant_leads', ['first_captured_at'])
    op.create_index('ix_applicant_leads_application_id', 'applicant_leads', ['application_id'])

    op.create_table(
        'applicant_lead_audit_logs',
        sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False),
        sa.Column('lead_id', sa.BigInteger(), nullable=False),
        sa.Column('admin_user_id', sa.BigInteger(), nullable=True),
        sa.Column('action', sa.String(length=40), nullable=False),
        sa.Column('detail', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['admin_user_id'], ['admin_users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_applicant_lead_audit_logs_lead_id', 'applicant_lead_audit_logs', ['lead_id'])


def downgrade():
    op.drop_index('ix_applicant_lead_audit_logs_lead_id', table_name='applicant_lead_audit_logs')
    op.drop_table('applicant_lead_audit_logs')
    op.drop_index('ix_applicant_leads_application_id', table_name='applicant_leads')
    op.drop_index('ix_applicant_leads_first_captured_at', table_name='applicant_leads')
    op.drop_index('ix_applicant_leads_lead_status', table_name='applicant_leads')
    op.drop_index('ix_applicant_leads_normalized_phone', table_name='applicant_leads')
    op.drop_table('applicant_leads')
