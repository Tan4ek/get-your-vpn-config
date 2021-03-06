"""extern traffic model

Revision ID: 36234bb79f75
Revises: 56001dbb442e
Create Date: 2022-05-09 17:44:44.790201

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '36234bb79f75'
down_revision = '56001dbb442e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('traffic_records', sa.Column('direction', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('traffic_records', 'direction')
    # ### end Alembic commands ###
