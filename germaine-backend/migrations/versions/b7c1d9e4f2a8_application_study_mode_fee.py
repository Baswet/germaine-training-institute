"""application study mode + server-calculated fee

Revision ID: b7c1d9e4f2a8
Revises: a1b2c3d4e5f6
"""
from alembic import op
import sqlalchemy as sa

revision = "b7c1d9e4f2a8"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("applications", sa.Column("study_mode", sa.String(length=20), nullable=True))
    op.add_column("applications", sa.Column("calculated_fee", sa.Numeric(10, 2), nullable=True))
    op.create_check_constraint(
        "ck_applications_study_mode",
        "applications",
        "study_mode IS NULL OR study_mode IN ('fulltime', 'parttime', 'distance', 'talented')",
    )


def downgrade():
    op.drop_constraint("ck_applications_study_mode", "applications", type_="check")
    op.drop_column("applications", "calculated_fee")
    op.drop_column("applications", "study_mode")