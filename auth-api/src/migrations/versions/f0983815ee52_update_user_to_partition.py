"""update_user_to_partition

Revision ID: f0983815ee52
Revises: e1d39ee8da8d
Create Date: 2022-03-14 20:00:26.165166

"""
# type: ignore
from alembic import op

# revision identifiers, used by Alembic.
revision = 'f0983815ee52'
down_revision = 'e1d39ee8da8d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_foreign_key(
        op.f('fk__users_auth_history_pc__user_id__users'),
        'users_auth_history_pc',
        'users',
        ['user_id'],
        ['id'],
        source_schema='auth',
        referent_schema='auth',
    )
    op.create_foreign_key(
        op.f('fk__users_auth_history_mobile__user_id__users'),
        'users_auth_history_mobile',
        'users',
        ['user_id'],
        ['id'],
        source_schema='auth',
        referent_schema='auth',
    )
    op.create_foreign_key(
        op.f('fk__users_auth_history_tablet__user_id__users'),
        'users_auth_history_tablet',
        'users',
        ['user_id'],
        ['id'],
        source_schema='auth',
        referent_schema='auth',
    )

    op.create_primary_key(
        op.f('pk__users_auth_history_pc'),
        'users_auth_history_pc',
        ['id', 'device'],
        schema='auth',
    )
    op.create_primary_key(
        op.f('pk__users_auth_history_mobile'),
        'users_auth_history_mobile',
        ['id', 'device'],
        schema='auth',
    )
    op.create_primary_key(
        op.f('pk__users_auth_history_tablet'),
        'users_auth_history_tablet',
        ['id', 'device'],
        schema='auth',
    )


def downgrade():
    op.drop_constraint(
        op.f('fk__users_auth_history_pc__user_id__users'),
        'users_auth_history_pc',
        type_='foreignkey',
        schema='auth',
    )
    op.drop_constraint(
        op.f('fk__users_auth_history_mobile__user_id__users'),
        'users_auth_history_mobile',
        type_='foreignkey',
        schema='auth',
    )
    op.drop_constraint(
        op.f('fk__users_auth_history_tablet__user_id__users'),
        'users_auth_history_tablet',
        type_='foreignkey',
        schema='auth',
    )
    op.drop_constraint(
        op.f('pk__users_auth_history_pc'),
        'users_auth_history_pc',
        type_='foreignkey',
        schema='auth',
    )
    op.drop_constraint(
        op.f('pk__users_auth_history_mobile'),
        'users_auth_history_mobile',
        type_='foreignkey',
        schema='auth',
    )
    op.drop_constraint(
        op.f('pk__users_auth_history_tablet'),
        'users_auth_history_tablet',
        type_='foreignkey',
        schema='auth',
    )
