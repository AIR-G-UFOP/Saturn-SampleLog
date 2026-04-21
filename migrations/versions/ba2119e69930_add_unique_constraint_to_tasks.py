"""add unique constraint to tasks

Revision ID: ba2119e69930
Revises: de6b78e3390e
Create Date: 2026-04-21 22:10:51.870723

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ba2119e69930'
down_revision: Union[str, Sequence[str], None] = 'de6b78e3390e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('tasks') as batch_op:
        batch_op.create_unique_constraint(
            'uq_task_identity',
            ['type', 'name', 'start_date', 'end_date'])


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("tasks") as batch_op:
        batch_op.drop_constraint(
            "uq_task_identity",
            type_="unique"
        )