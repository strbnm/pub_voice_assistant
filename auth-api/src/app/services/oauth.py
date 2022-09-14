from flask import Request

from app.database import session_scope
from app.datastore import user_datastore
from app.errors import AccountsServiceError, OAuthServiceError
from app.models.oauth import SocialAccount
from app.models.roles import ProtectedRoleEnum
from app.services.auth import AccountsService
from app.utils import traced


class OauthService:
    def __init__(
        self, social_name: str, social_id: str, user_name: str, user_email: str
    ) -> None:
        self.social_name = social_name
        self.social_id = social_id
        self.user_name = user_name
        self.user_email = user_email

    @traced('OauthService.login')
    def login(self, request: Request) -> tuple[str, str]:
        with session_scope():
            social_account = SocialAccount.get_or_create(
                social_id=self.social_id,
                social_name=self.social_name,
                user_name=self.user_name,
                user_email=self.user_email,
            )
            user_datastore.add_role_to_user(social_account.user, ProtectedRoleEnum.guest.value)
        try:
            account_service = AccountsService(social_account.user)
            access_token, refresh_token = account_service.login(request)
        except AccountsServiceError as account_err:
            raise OAuthServiceError from account_err
        return access_token, refresh_token
