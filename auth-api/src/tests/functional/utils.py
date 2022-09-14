from datetime import datetime
from typing import Optional, Union
from uuid import UUID

from jose import JWTError, jwt
from pydantic import BaseModel

from app.models.roles import ProtectedRoleEnum
from app.settings.config import settings


class BaseTokenData(BaseModel):
    fresh: bool
    iat: datetime
    jti: str
    type: str
    sub: str
    nbf: datetime
    exp: datetime


class AccessTokenData(BaseTokenData):
    """Модель полей access-токена"""

    is_admin: bool
    is_staff: bool
    roles: list[str]


class RefreshTokenData(BaseTokenData):
    """Модель полей refresh-токена"""


def decode_jwt(token: str) -> Union[AccessTokenData, RefreshTokenData]:
    try:
        decoded_token = jwt.decode(token, settings.JWT.SECRET_KEY, algorithms=['HS256'])
        if decoded_token['type'] == 'access':
            return AccessTokenData(**decoded_token)
        elif decoded_token['type'] == 'refresh':
            return RefreshTokenData(**decoded_token)
    except JWTError:
        pass


class UserTestModel(BaseModel):
    id: UUID
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    active: bool
    is_admin: bool = False
    is_staff: bool = False
    roles_list: list[str] = [ProtectedRoleEnum.guest.value]


class UserSignupResponseModel(BaseModel):
    id: UUID
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: bool
    created_at: datetime
