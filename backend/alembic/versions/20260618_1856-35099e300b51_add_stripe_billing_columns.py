"""add stripe billing columns

Revision ID: 35099e300b51
Revises: 82bf36cfd7f0
Create Date: 2026-06-18 18:56:54.570126

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "35099e300b51"
down_revision: Union[str, None] = "82bf36cfd7f0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("stripe_customer_id", sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column("stripe_subscription_id", sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column("subscription_status", sa.String(length=32), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("subscription_status")
        batch_op.drop_column("stripe_subscription_id")
        batch_op.drop_column("stripe_customer_id")
