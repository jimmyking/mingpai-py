"""empty message

Revision ID: 467c2cc7c559
Revises: 182cf03224d6
Create Date: 2014-10-23 17:27:30.965788

"""

# revision identifiers, used by Alembic.
revision = '467c2cc7c559'
down_revision = '182cf03224d6'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('issue_types',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_issue_types_name'), 'issue_types', ['name'], unique=True)
    op.create_table('order_types',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_order_types_name'), 'order_types', ['name'], unique=True)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_order_types_name'), table_name='order_types')
    op.drop_table('order_types')
    op.drop_index(op.f('ix_issue_types_name'), table_name='issue_types')
    op.drop_table('issue_types')
    ### end Alembic commands ###
