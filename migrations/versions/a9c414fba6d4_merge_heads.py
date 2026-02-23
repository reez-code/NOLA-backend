"""Merge heads

Revision ID: a9c414fba6d4
Revises: add_job_details_001, a9d497823bfa
Create Date: 2026-02-23 16:45:48.416758

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a9c414fba6d4'
down_revision = ('add_job_details_001', 'a9d497823bfa')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
