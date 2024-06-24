"""add created_at field for actions

Revision ID: 7d488b5a9a39
Revises: 4be2150f205a
Create Date: 2024-06-02 12:57:39.494250

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7d488b5a9a39'
down_revision: Union[str, None] = '4be2150f205a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('releases')
    op.drop_table('release_action_approvals')
    op.drop_table('release_actions')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('release_actions',
    sa.Column('id', sa.NUMERIC(), nullable=False),
    sa.Column('release_id', sa.INTEGER(), nullable=False),
    sa.Column('env', sa.VARCHAR(length=10), nullable=False),
    sa.Column('tag_url', sa.VARCHAR(length=127), nullable=False),
    sa.Column('comment', sa.VARCHAR(length=127), nullable=False),
    sa.Column('version', sa.VARCHAR(length=15), nullable=False),
    sa.Column('deployment_status', sa.VARCHAR(length=7), nullable=False),
    sa.Column('action_url', sa.VARCHAR(length=127), nullable=False),
    sa.ForeignKeyConstraint(['release_id'], ['releases.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('action_url'),
    sa.UniqueConstraint('version', 'env', name='uq_version_env')
    )
    op.create_table('release_action_approvals',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('release_action_id', sa.NUMERIC(), nullable=False),
    sa.Column('approved_by', sa.VARCHAR(), nullable=False),
    sa.ForeignKeyConstraint(['release_action_id'], ['release_actions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('releases',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=127), nullable=False),
    sa.Column('state', sa.VARCHAR(length=8), nullable=True),
    sa.Column('created_on', sa.TIMESTAMP(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
