"""add hash

Revision ID: d22fe05901c7
Revises: 7e3312510519
Create Date: 2022-02-28 09:09:46.803050

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd22fe05901c7'
down_revision = '7e3312510519'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('datacenter', schema=None) as batch_op:
        batch_op.add_column(sa.Column('hash', sa.String(length=32), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('datacenter', schema=None) as batch_op:
        batch_op.drop_column('hash')

    # ### end Alembic commands ###
