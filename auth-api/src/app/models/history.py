from enum import Enum
from uuid import uuid4

from sqlalchemy.dialects.postgresql import ENUM, UUID

from app.database import db
from app.models.mixin import TimestampMixin


class PlatformEnum(Enum):
    pc = 'pc'
    mobile = 'mobile'
    tablet = 'tablet'


class HistoryUserAuth(TimestampMixin, db.Model):
    __tablename__ = 'users_auth_history'
    __table_args__ = (db.PrimaryKeyConstraint('id', 'device'),)

    id = db.Column(UUID(as_uuid=True), default=uuid4, nullable=False)
    user_id = db.Column('user_id', UUID(as_uuid=True), db.ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    user_agent = db.Column(db.Text, nullable=False)
    ip_addr = db.Column(db.String(100))
    device = db.Column(db.Text)
    platform = db.Column(
        ENUM(PlatformEnum), nullable=False, server_default=PlatformEnum.pc.value
    )
    user = db.relationship('User', backref=db.backref('users_auth_history', lazy=True))
