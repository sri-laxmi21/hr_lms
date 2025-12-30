"""remove frame work field in test_reports table

Revision ID: fc20b1fdeb0d
Revises: a56076ac653b
Create Date: 2025-12-29 11:44:29.092859

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fc20b1fdeb0d'
down_revision: Union[str, Sequence[str], None] = 'a56076ac653b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.drop_column('test_reports', 'framework')


def downgrade() -> None:
    op.add_column('test_reports', sa.Column('framework', sa.String(length=255), nullable=True))
