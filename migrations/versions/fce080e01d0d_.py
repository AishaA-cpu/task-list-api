"""empty message

Revision ID: fce080e01d0d
Revises: 87a971db8e45
Create Date: 2021-12-04 19:27:01.266137

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fce080e01d0d'
down_revision = '87a971db8e45'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('task', sa.Column('completed_at', sa.DateTime(), nullable=True))
    op.add_column('task', sa.Column('description', sa.String(), nullable=True))
    op.add_column('task', sa.Column('title', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('task', 'title')
    op.drop_column('task', 'description')
    op.drop_column('task', 'completed_at')
    # ### end Alembic commands ###
