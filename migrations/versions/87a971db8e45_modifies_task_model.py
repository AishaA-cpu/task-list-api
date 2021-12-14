"""modifies task model

Revision ID: 87a971db8e45
Revises: a053b04a2a16
Create Date: 2021-12-04 17:35:32.152979

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '87a971db8e45'
down_revision = 'a053b04a2a16'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('task', sa.Column('task_id', sa.Integer(), nullable=False))
    # op.add_column('task', sa.Column('task_id', sa.Integer(), autoincrement=True, nullable=False))
    #op.drop_column('task', 'id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('task', sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_column('task', 'task_id')
    # ### end Alembic commands ###
