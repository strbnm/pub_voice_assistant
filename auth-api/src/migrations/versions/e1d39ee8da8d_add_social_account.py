"""add-social-account

Revision ID: e1d39ee8da8d
Revises: 48d7e8a37706
Create Date: 2022-03-12 08:31:48.181241

"""
# type: ignore
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e1d39ee8da8d'
down_revision = '48d7e8a37706'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'social_accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('social_id', sa.String(length=255), nullable=False),
        sa.Column('social_name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(
            ['user_id'], ['auth.users.id'], name=op.f('fk__social_accounts__user_id__users')
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk__social_accounts')),
        sa.UniqueConstraint('id'),
        sa.UniqueConstraint('social_id', 'social_name'),
        schema='auth',
    )
    op.execute(
        """CREATE TABLE IF NOT EXISTS auth."users_auth_history_pc"
                  PARTITION OF auth."users_auth_history" FOR VALUES IN ('pc');"""
    )

    op.execute(
        """CREATE TABLE IF NOT EXISTS auth."users_auth_history_mobile"
                  PARTITION OF auth."users_auth_history" FOR VALUES IN ('mobile');"""
    )

    op.execute(
        """CREATE TABLE IF NOT EXISTS auth."users_auth_history_tablet"
                  PARTITION OF auth."users_auth_history" FOR VALUES IN ('tablet');"""
    )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('social_accounts', schema='auth')
    op.drop_table('users_auth_history_pc', schema='auth')
    op.drop_table('users_auth_history_mobile', schema='auth')
    op.drop_table('users_auth_history_tablet', schema='auth')
    # ### end Alembic commands ###
