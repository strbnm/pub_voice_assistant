from uuid import uuid4

from sqlalchemy.dialects.postgresql import UUID

from app.database import db, session_scope
from app.models.mixin import TimestampMixin
from app.models.user import User


class SocialAccount(TimestampMixin, db.Model):
    __tablename__ = 'social_accounts'
    __table_args__ = (db.UniqueConstraint('social_id', 'social_name'),)

    id = db.Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, nullable=False
    )
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    social_id = db.Column(db.String(255), nullable=False)
    social_name = db.Column(db.String(255), nullable=False)

    user = db.relationship(User, backref=db.backref('social_accounts', lazy=True))

    def __str__(self) -> str:
        return f'<SocialAccount {self.social_name}:{self.user_id}>'

    @classmethod
    def get_or_create(
        cls, social_id: str, social_name: str, user_name: str, user_email: str
    ) -> 'SocialAccount':
        social_acc = cls.query.filter_by(social_id=social_id, social_name=social_name,).first()

        if not social_acc:
            user = User.get_or_create(user_name, user_email)

            with session_scope() as session:
                social_acc = cls(
                    social_id=social_id, social_name=social_name, user_id=user.id,
                )
                session.add(social_acc)

        return social_acc
