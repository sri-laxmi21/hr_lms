"""create subscription_plan_modules table

Revision ID: a37d3b334889
Revises: b9b845bcd0a7
Create Date: 2026-01-03
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "a37d3b334889"
down_revision: Union[str, Sequence[str], None] = "b9b845bcd0a7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "subscription_plan_modules",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "plan_id",
            sa.Integer,
            sa.ForeignKey("subscription_plans.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "module_id",
            sa.Integer,
            sa.ForeignKey("modules.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.UniqueConstraint("plan_id", "module_id", name="uq_plan_module"),
    )


def downgrade() -> None:
    op.drop_table("subscription_plan_modules")
