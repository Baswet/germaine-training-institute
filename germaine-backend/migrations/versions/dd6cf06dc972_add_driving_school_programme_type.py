"""add driving_school programme_type + fee_amount column

Revision ID: dd6cf06dc972
Revises: c4d7f9a1b2e6
Create Date: 2026-08-25

Additive, non-destructive schema change (Step 2026-08-25 addendum):

1. Widens the programmes.programme_type CHECK constraint from
   ('academic', 'ai_bootcamp') to also allow 'driving_school'.
2. Adds a nullable programmes.fee_amount NUMERIC(10,2) column used
   exclusively for driving_school pricing (individual per-programme fee,
   since driving_school rows have no parent School and no ProgrammeMode
   rows). NULL for existing academic and ai_bootcamp rows - their pricing
   continues to come from School.fee and ProgrammeMode.fee_amount
   respectively, completely unchanged.

No existing tables are dropped. No existing rows are modified, deleted,
or reinterpreted. No foreign keys are altered. Downgrade reverses in the
opposite order and will correctly fail (by design) if any driving_school
row still exists, since the original 2-value CHECK constraint cannot
accept 'driving_school' rows.
"""
from alembic import op
import sqlalchemy as sa

revision = 'dd6cf06dc972'
down_revision = 'c4d7f9a1b2e6'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('ck_programmes_programme_type', 'programmes', type_='check')
    op.create_check_constraint(
        'ck_programmes_programme_type',
        'programmes',
        "programme_type IN ('academic', 'ai_bootcamp', 'driving_school')",
    )
    op.add_column('programmes', sa.Column('fee_amount', sa.Numeric(10, 2), nullable=True))


def downgrade():
    op.drop_column('programmes', 'fee_amount')
    op.drop_constraint('ck_programmes_programme_type', 'programmes', type_='check')
    op.create_check_constraint(
        'ck_programmes_programme_type',
        'programmes',
        "programme_type IN ('academic', 'ai_bootcamp')",
    )
