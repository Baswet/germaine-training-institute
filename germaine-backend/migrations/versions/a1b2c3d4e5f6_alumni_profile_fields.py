"""alumni profile fields (course, employment status, occupation)

Revision ID: a1b2c3d4e5f6
Revises: f3a9c7e21b04
"""
from alembic import op
import sqlalchemy as sa

revision = "a1b2c3d4e5f6"
down_revision = "f3a9c7e21b04"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("alumni", sa.Column("course", sa.String(length=200), nullable=True))
    op.add_column("alumni", sa.Column("employment_status", sa.String(length=20), nullable=True))
    op.add_column("alumni", sa.Column("occupation", sa.String(length=200), nullable=True))
    op.create_check_constraint(
        "ck_alumni_employment_status",
        "alumni",
        "employment_status IS NULL OR employment_status IN ('employed', 'unemployed', 'self_employed', 'studying')",
    )


def downgrade():
    op.drop_constraint("ck_alumni_employment_status", "alumni", type_="check")
    op.drop_column("alumni", "occupation")
    op.drop_column("alumni", "employment_status")
    op.drop_column("alumni", "course")