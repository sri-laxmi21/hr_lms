"""merge multiple heads

Revision ID: 79878089200d
Revises: 05e9d936f3cc, 13d2d7cea878
Create Date: 2025-12-23 12:44:03.039867

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '79878089200d'
down_revision: Union[str, Sequence[str], None] = ('05e9d936f3cc', '13d2d7cea878')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
