"""empty message

Revision ID: fee80b6a19d4
Revises: 
Create Date: 2020-05-03 11:58:28.865137

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fee80b6a19d4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('evaluations',
    sa.Column('index', sa.Integer(), nullable=False),
    sa.Column('send_time', sa.DateTime(), nullable=True),
    sa.Column('react_time', sa.DateTime(), nullable=True),
    sa.Column('match_index', sa.Integer(), nullable=True),
    sa.Column('user_index', sa.Integer(), nullable=True),
    sa.Column('mate_index', sa.Integer(), nullable=True),
    sa.Column('satisfaction', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['match_index'], ['matches.index'], ),
    sa.ForeignKeyConstraint(['mate_index'], ['users.index'], ),
    sa.ForeignKeyConstraint(['user_index'], ['users.index'], ),
    sa.PrimaryKeyConstraint('index')
    )
    # ### end Alembic commands ###
