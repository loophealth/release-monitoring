"""setup_testing_statues

Revision ID: 67c62fd42bc2
Revises: 7d488b5a9a39
Create Date: 2024-06-22 12:45:17.288058

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '67c62fd42bc2'
down_revision: Union[str, None] = '7d488b5a9a39'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###