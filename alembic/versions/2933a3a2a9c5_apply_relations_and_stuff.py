"""apply relations and stuff

Revision ID: 2933a3a2a9c5
Revises: da594a4f23fc
Create Date: 2024-06-01 17:22:08.991116

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2933a3a2a9c5'
down_revision: Union[str, None] = 'da594a4f23fc'
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