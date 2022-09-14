import pytest

from app.database import session_scope
from app.datastore import user_datastore
from app.models.roles import ProtectedRoleEnum, Role
from app.services.auth import AccountsService
from tests.functional.utils import UserTestModel


def create_user(app, username, password, email, role, is_admin=False, is_staff=False):
    with app.app_context():
        with session_scope():
            user = user_datastore.create_user(
                username=username, password=password, email=email
            )
            user_datastore.add_role_to_user(user, role.name)
            return UserTestModel(
                **user.__dict__, is_admin=is_admin, is_staff=is_staff, roles_list=[role.name]
            )


@pytest.fixture
def temp_user_username():
    return 'test'


@pytest.fixture
def temp_staff_user_username():
    return 'test_staff'


@pytest.fixture
def temp_superuser_username():
    return 'test_admin'


@pytest.fixture
def temp_user_email():
    return 'test@example.com'


@pytest.fixture
def temp_staff_user_email():
    return 'test_staff@example.com'


@pytest.fixture
def temp_superuser_email():
    return 'test_admin@example.com'


@pytest.fixture
def temp_user_password():
    return '#Test1234#'


@pytest.fixture
def temp_user_jwt_pair(temp_user) -> tuple[str, str]:
    account_service = AccountsService(temp_user)
    return account_service.get_token_pair()


@pytest.fixture
def temp_staff_user_jwt_pair(temp_staff_user) -> tuple[str, str]:
    account_service = AccountsService(temp_staff_user)
    return account_service.get_token_pair()


@pytest.fixture
def temp_superuser_jwt_pair(temp_superuser) -> tuple[str, str]:
    account_service = AccountsService(temp_superuser)
    return account_service.get_token_pair()


@pytest.fixture
def temp_user_auth_access_header(temp_user_jwt_pair) -> dict[str, str]:
    access_token, _ = temp_user_jwt_pair
    return {'Authorization': f'Bearer {access_token}'}


@pytest.fixture
def temp_staff_user_auth_access_header(temp_staff_user_jwt_pair) -> dict[str, str]:
    access_token, _ = temp_staff_user_jwt_pair
    return {'Authorization': f'Bearer {access_token}'}


@pytest.fixture
def temp_superuser_auth_access_header(temp_superuser_jwt_pair) -> dict[str, str]:
    access_token, _ = temp_superuser_jwt_pair
    return {'Authorization': f'Bearer {access_token}'}


@pytest.fixture
def temp_user_auth_refresh_header(temp_user_jwt_pair) -> dict[str, str]:
    _, refresh_token = temp_user_jwt_pair
    return {'Authorization': f'Bearer {refresh_token}'}


@pytest.fixture
def temp_staff_user_auth_refresh_header(temp_staff_user_jwt_pair) -> dict[str, str]:
    _, refresh_token = temp_staff_user_jwt_pair
    return {'Authorization': f'Bearer {refresh_token}'}


@pytest.fixture
def temp_superuser_auth_refresh_header(temp_superuser_jwt_pair) -> dict[str, str]:
    _, refresh_token = temp_superuser_jwt_pair
    return {'Authorization': f'Bearer {refresh_token}'}


@pytest.fixture
def temp_user(app, temp_user_username, temp_user_password, temp_user_email, guest_role):
    return create_user(
        app, temp_user_username, temp_user_password, temp_user_email, guest_role
    )


@pytest.fixture
def temp_staff_user(
    app, temp_staff_user_username, temp_user_password, temp_staff_user_email, staff_role
):
    return create_user(
        app,
        temp_staff_user_username,
        temp_user_password,
        temp_staff_user_email,
        staff_role,
        is_staff=True,
    )


@pytest.fixture
def temp_superuser(
    app, temp_superuser_username, temp_user_password, temp_superuser_email, superuser_role
):
    return create_user(
        app,
        temp_superuser_username,
        temp_user_password,
        temp_superuser_email,
        superuser_role,
        is_admin=True,
    )


@pytest.fixture
def guest_role() -> Role:
    return Role.query.filter_by(name=ProtectedRoleEnum.guest.value).one_or_none()


@pytest.fixture
def superuser_role() -> Role:
    return Role.query.filter_by(name=ProtectedRoleEnum.superuser.value).one_or_none()


@pytest.fixture
def staff_role() -> Role:
    return Role.query.filter_by(name=ProtectedRoleEnum.staff.value).one_or_none()
