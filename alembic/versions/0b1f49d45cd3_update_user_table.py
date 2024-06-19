"""update user table

Revision ID: 0b1f49d45cd3
Revises: 6afea8b902fb
Create Date: 2024-06-18 20:57:33.515818

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0b1f49d45cd3'
down_revision: Union[str, None] = '6afea8b902fb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('clients', 'role')
    op.add_column('users', sa.Column('role', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'role')
    op.add_column('clients', sa.Column('role', sa.VARCHAR(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
