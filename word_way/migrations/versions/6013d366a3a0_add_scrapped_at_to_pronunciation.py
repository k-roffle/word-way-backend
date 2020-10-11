"""Add scrapped_at to Pronunciation

Revision ID: 6013d366a3a0
Revises: 94abc68d90ce
Create Date: 2020-10-11 16:39:21.931294

"""
from alembic import op
from sqlalchemy import Column, DateTime

revision = '6013d366a3a0'
down_revision = '94abc68d90ce'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'pronunciation',
        Column('scrapped_at', DateTime(timezone=True), nullable=True)
    )


def downgrade():
    op.drop_column('pronunciation', 'scrapped_at')
