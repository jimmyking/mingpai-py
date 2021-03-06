"""empty message

Revision ID: 36a575108d1e
Revises: 342555c635c
Create Date: 2014-10-29 09:17:57.297972

"""

# revision identifiers, used by Alembic.
revision = '36a575108d1e'
down_revision = '342555c635c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('order_group_tasks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('group_id', sa.Integer(), nullable=True),
    sa.Column('task_id', sa.Integer(), nullable=True),
    sa.Column('create_man', sa.Integer(), nullable=True),
    sa.Column('create_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['create_man'], ['users.id'], ),
    sa.ForeignKeyConstraint(['group_id'], ['order_groups.id'], ),
    sa.ForeignKeyConstraint(['task_id'], ['group_tasks.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_order_group_tasks_create_date'), 'order_group_tasks', ['create_date'], unique=False)
    op.create_table('order_tasks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.Column('task_id', sa.Integer(), nullable=True),
    sa.Column('create_man', sa.Integer(), nullable=True),
    sa.Column('create_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['create_man'], ['users.id'], ),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
    sa.ForeignKeyConstraint(['task_id'], ['group_tasks.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_order_tasks_create_date'), 'order_tasks', ['create_date'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_order_tasks_create_date'), table_name='order_tasks')
    op.drop_table('order_tasks')
    op.drop_index(op.f('ix_order_group_tasks_create_date'), table_name='order_group_tasks')
    op.drop_table('order_group_tasks')
    ### end Alembic commands ###
