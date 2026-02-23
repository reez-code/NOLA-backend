"""Add profession and business_category fields

Revision ID: add_profession_and_category
Revises: 
Create Date: 2026-02-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_profession_and_category'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add profession column to developer_profiles
    op.add_column('developer_profiles', sa.Column('profession', sa.String(150), nullable=True))
    
    # Add business_category column to client_profiles
    op.add_column('client_profiles', sa.Column('business_category', sa.String(150), nullable=True))


def downgrade():
    # Remove profession column from developer_profiles
    op.drop_column('developer_profiles', 'profession')
    
    # Remove business_category column from client_profiles
    op.drop_column('client_profiles', 'business_category')
