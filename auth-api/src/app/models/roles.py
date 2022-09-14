from enum import Enum
from uuid import uuid4

from flask_security import RoleMixin
from sqlalchemy.dialects.postgresql import UUID

from app.database import db
from app.models.mixin import TimestampMixin


class ProtectedRoleEnum(Enum):
    guest = 'guest'
    staff = 'staff'
    superuser = 'superuser'


class Role(TimestampMixin, db.Model, RoleMixin):
    __tablename__ = 'roles'

    id = db.Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, nullable=False
    )
    name = db.Column(db.String(50), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return f'<Role {self.name}>'

    class Meta:
        PROTECTED_ROLE_NAMES = (
            ProtectedRoleEnum.guest.value,
            ProtectedRoleEnum.staff.value,
            ProtectedRoleEnum.superuser.value,
        )


class RolesUsers(db.Model):
    __tablename__ = 'roles_users'

    id = db.Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, nullable=False
    )
    user_id = db.Column(
        'user_id', UUID(as_uuid=True), db.ForeignKey('users.id', ondelete='CASCADE')
    )
    role_id = db.Column(
        'role_id', UUID(as_uuid=True), db.ForeignKey('roles.id', ondelete='CASCADE')
    )
    created_at = db.Column(db.DateTime, server_default=db.func.now())
