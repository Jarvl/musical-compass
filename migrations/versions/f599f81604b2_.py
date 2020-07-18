"""empty message

Revision ID: f599f81604b2
Revises: 121b0d3c9a81
Create Date: 2020-07-17 15:47:12.917398

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f599f81604b2'
down_revision = '121b0d3c9a81'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('result__track', sa.Column('track_order', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('result__track', 'track_order')
    # ### end Alembic commands ###
