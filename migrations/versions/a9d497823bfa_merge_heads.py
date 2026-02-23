"""Merge heads

Revision ID: a9d497823bfa
Revises: add_exp_points_001, add_profession_and_category
Create Date: 2026-02-17 17:15:03.045362

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a9d497823bfa'
down_revision = ('add_exp_points_001', 'add_profession_and_category')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
