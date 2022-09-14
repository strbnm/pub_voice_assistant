from typing import Optional
from uuid import uuid4

from flask_security import UserMixin
from sqlalchemy.dialects.postgresql import UUID
from werkzeug.security import check_password_hash, generate_password_hash

from app.database import db, session_scope
from app.models.mixin import TimestampMixin
from app.models.roles import ProtectedRoleEnum


class User(TimestampMixin, db.Model, UserMixin):
    __tablename__ = 'users'
    __table_args__ = (db.UniqueConstraint('email', 'username'),)

    id = db.Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, nullable=False
    )
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    _password = db.Column('password', db.String(255), nullable=False)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    active = db.Column(db.Boolean())
    roles = db.relationship(
        'Role', secondary='auth.roles_users', backref=db.backref('users', lazy='dynamic'),
    )

    def __str__(self) -> str:
        return f'<User {self.username}>'

    @property
    def password(self) -> str:
        return self._password

    @password.setter
    def password(self, password: str) -> None:
        self._password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self._password, password)

    @property
    def is_admin(self) -> bool:
        return self.has_role(ProtectedRoleEnum.superuser.value)

    @property
    def is_staff(self) -> bool:
        return self.has_role(ProtectedRoleEnum.staff.value)

    @property
    def roles_list(self) -> list[str]:
        return [role.name for role in self.roles]

    @classmethod
    def get_or_create(cls, username: str, email: str) -> Optional['User']:
        from app.datastore import user_datastore

        user = cls.query.filter(db.and_(cls.username == username, cls.email == email,)).first()

        if not user:
            with session_scope():
                user = user_datastore.create_user(
                    username=username, email=email, password=str(uuid4()),
                )
        return user
