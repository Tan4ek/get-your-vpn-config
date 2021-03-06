"""traffic model

Revision ID: 56001dbb442e
Revises: cd4c37ebabe2
Create Date: 2022-04-16 23:52:52.021117

"""
import uuid

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '56001dbb442e'
down_revision = 'cd4c37ebabe2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("ALTER TABLE provider RENAME TO providers")
    op.execute("ALTER TABLE invite_code RENAME TO invite_codes")
    op.create_table('traffic_records',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('date_from', sa.Integer(), nullable=False),
                    sa.Column('date_to', sa.Integer(), nullable=False),
                    sa.Column('provider_id', sa.String(), nullable=False),
                    sa.Column('quantity_bytes', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['provider_id'], ['providers.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index('idx_from_to', 'traffic_records', ['date_from', 'date_to'], unique=False)
    op.execute("ALTER TABLE providers ADD COLUMN external_id VARCHAR NOT NULL DEFAULT ''")
    op.execute("UPDATE providers SET external_id = substr(payload,20,36) WHERE type='openvpn'")
    op.create_index(op.f('idx_provider_external_id'), 'providers', ['external_id'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('idx_provider_external_id'), table_name='providers')
    op.drop_column('providers', 'external_id')
    op.drop_index('idx_from_to', table_name='traffic_records')
    op.drop_table('traffic_records')
    # ### end Alembic commands ###
