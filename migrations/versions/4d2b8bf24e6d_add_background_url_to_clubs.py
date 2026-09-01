"""Add background_url to clubs

Revision ID: 4d2b8bf24e6d
Revises: e687d3ce1b09
Create Date: 2026-09-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4d2b8bf24e6d"
down_revision = "e687d3ce1b09"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("clubs", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("background_url", sa.String(length=255), nullable=True))


def downgrade():
    with op.batch_alter_table("clubs", schema=None) as batch_op:
        batch_op.drop_column("background_url")
