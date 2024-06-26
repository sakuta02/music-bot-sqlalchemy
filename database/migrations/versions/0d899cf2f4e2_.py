"""empty message

Revision ID: 0d899cf2f4e2
Revises: 
Create Date: 2024-03-31 16:33:26.914835

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0d899cf2f4e2'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('artists',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=48), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("(now() at time zone 'utc')"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text("(now() at time zone 'utc')"), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("(now() at time zone 'utc')"), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('music',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=48), nullable=False),
    sa.Column('artist_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('file_id', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("(now() at time zone 'utc')"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text("(now() at time zone 'utc')"), nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['artists.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], onupdate='CASCADE', ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('library',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('music_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("(now() at time zone 'utc')"), nullable=False),
    sa.ForeignKeyConstraint(['music_id'], ['music.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'music_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('library')
    op.drop_table('music')
    op.drop_table('users')
    op.drop_table('artists')
    # ### end Alembic commands ###
