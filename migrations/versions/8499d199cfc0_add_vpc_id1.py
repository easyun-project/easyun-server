"""add vpc_id1

Revision ID: 8499d199cfc0
Revises: 
Create Date: 2021-12-13 22:20:21.216456

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8499d199cfc0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('datacenter', schema=None) as batch_op:
        batch_op.add_column(sa.Column('vpc_id1', sa.String(length=120), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('datacenter', schema=None) as batch_op:
        batch_op.drop_column('vpc_id1')

    # ### end Alembic commands ###
