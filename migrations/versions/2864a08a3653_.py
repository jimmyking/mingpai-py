"""empty message

Revision ID: 2864a08a3653
Revises: 545328e43161
Create Date: 2014-10-25 00:07:32.813019

"""

# revision identifiers, used by Alembic.
revision = '2864a08a3653'
down_revision = '545328e43161'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('orders', sa.Column('is_delete', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('orders', 'is_delete')
    ### end Alembic commands ###
