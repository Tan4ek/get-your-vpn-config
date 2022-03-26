"""init

Revision ID: cd4c37ebabe2
Revises: 
Create Date: 2022-03-26 23:00:51.880502

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'cd4c37ebabe2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('invite_code',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('code', sa.String(), nullable=False),
                    sa.Column('description', sa.String(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('code')
                    )
    op.create_table('provider',
                    sa.Column('id', sa.String(), nullable=False),
                    sa.Column('type', sa.String(), nullable=False),
                    sa.Column('invite_code_id', sa.Integer(), nullable=False),
                    sa.Column('payload', sa.JSON(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.ForeignKeyConstraint(['invite_code_id'], ['invite_code.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('provider')
    op.drop_table('invite_code')
    # ### end Alembic commands ###
