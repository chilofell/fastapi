"""empty message

Revision ID: 48df149ff37a
Revises: c520341f1115
Create Date: 2024-06-05 20:15:13.509056

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '48df149ff37a'
down_revision: Union[str, None] = 'c520341f1115'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    op.add_column('devices', sa.Column('scale_value', sa.Integer(), nullable=True))
    op.drop_column('devices', 'value')
    op.add_column('users', sa.Column('city', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'city')
    op.add_column('devices', sa.Column('value', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_column('devices', 'scale_value')
    op.create_table('user',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('email', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('username', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('hashed_password', sa.VARCHAR(length=1024), autoincrement=False, nullable=False),
    sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('is_superuser', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('is_verified', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='user_pkey')
    )
    # ### end Alembic commands ###
