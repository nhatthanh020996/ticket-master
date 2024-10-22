"""empty message

Revision ID: 6829d50fa10a
Revises: 
Create Date: 2024-09-23 21:49:57.039992

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
import sqlalchemy_utils

from app.users.enums import IGenderEnum


# revision identifiers, used by Alembic.
revision = '6829d50fa10a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('roles',
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=10), nullable=False),
    sa.Column('desc', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_roles_id'), 'roles', ['id'], unique=False)
    op.create_table('users',
    sa.Column('username', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('phone', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('gender', sqlalchemy_utils.types.choice.ChoiceType(IGenderEnum), nullable=True),
    sa.Column('birthdate', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('hashed_password', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_user_id'), 'users', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_id'), table_name='user')
    op.drop_table('users')
    op.drop_index(op.f('ix_roles_id'), table_name='roles')
    op.drop_table('roles')
    # ### end Alembic commands ###
