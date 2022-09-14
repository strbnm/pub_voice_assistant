from http import HTTPStatus
from logging import getLogger

from flask import jsonify, request, url_for
from flask_jwt_extended import current_user, get_jwt, jwt_required
from flask_restx import Resource

from app.api.v1.account import namespace
from app.api.v1.account.parsers import (
    authorization_parser,
    login_request_parser,
    signup_request_parser,
)
from app.api.v1.account.schemes import LogInArgs, signup_response
from app.database import session_scope, db
from app.datastore import user_datastore
from app.errors import APIConflictError, ErrorsMessages, APIBadRequestError
from app.models.roles import ProtectedRoleEnum
from app.models.user import User
from app.services.auth import AccountsService
from app.utils import (
    error_processing,
    generate_confirmation_token,
    confirm_token,
    send_notification,
)


@namespace.route('/signup')
class SignUpView(Resource):
    @namespace.doc(
        'signup',
        responses={
            201: 'Пользователь создан',
            400: 'Отсутствует обязательное поле или недостаточная длина пароля',
            409: 'Пользователь с таким адресом электронной почты уже существует!',
        },
    )
    @namespace.expect(signup_request_parser)
    @namespace.marshal_with(signup_response, code=HTTPStatus.CREATED)
    @error_processing(getLogger('SignUpAPIView.post'))
    def post(self):
        """Регистрация пользователя"""
        args = signup_request_parser.parse_args()
        user = User.query.filter_by(email=args['email']).one_or_none()
        if user:
            raise APIConflictError(ErrorsMessages.EMAIL_IS_BUSY.value, args['email'])
        with session_scope():
            new_user = user_datastore.create_user(**args, confirmed=False)
            user_datastore.add_role_to_user(new_user, ProtectedRoleEnum.guest.value)
        token = generate_confirmation_token(new_user.email)
        confirm_url = url_for('Account_confirm_email_view', token=token, _external=True)
        payload = {
            'user_id': str(new_user.id),
            'user_email': new_user.email,
            'username': new_user.username,
            'first_name': new_user.first_name,
            'last_name': new_user.last_name,
            'token': token,
            'callback_url': confirm_url,
        }

        send_notification(payload)

        return new_user, HTTPStatus.CREATED


@namespace.route('/confirm/<string:token>')
class ConfirmEmailView(Resource):
    @namespace.doc(
        'confirm email',
        responses={
            200: 'E-mail успешно подтвержден.',
            208: 'E-mail уже подтвержден.',
            400: 'Ссылка для подтверждения недействительна или срок ее действия истек.',
        },
    )
    @namespace.expect(authorization_parser)
    @error_processing(getLogger('ConfirmEmailView.post'))
    @jwt_required()
    def post(self, token):
        """Проверка токена"""
        email = confirm_token(token)
        if not email:
            raise APIBadRequestError(ErrorsMessages.BAD_SIGNATURE.value)
        if email != current_user.email:
            return (
                'Подтверждаемый e-mail не совпадает с текущим аккаунтом.',
                HTTPStatus.BAD_REQUEST,
            )
        if current_user.confirmed:
            return 'E-mail уже подтвержден.', HTTPStatus.ALREADY_REPORTED
        else:
            with session_scope():
                current_user.confirmed = True
                current_user.confirmed_on = db.func.now()
                user_datastore.commit()
            return jsonify(message='E-mail успешно подтвержден.')


@namespace.route('/login')
class LoginView(Resource):
    @namespace.doc(
        'login',
        responses={200: 'Авторизация успешна', 401: 'Неверное имя пользователя или пароль'},
    )
    @namespace.expect(login_request_parser)
    @error_processing(getLogger('LoginAPIView.post'))
    @jwt_required(optional=True)
    def post(self):
        """Авторизация пользователя в системе"""
        if current_user:
            return jsonify(f'Пользователь {current_user.email} уже аутентифицирован')

        args = LogInArgs(**login_request_parser.parse_args())
        user = AccountsService.get_authorized_user(email=args.login, password=args.password,)
        accounts_service = AccountsService(user)
        access_token, refresh_token = accounts_service.login(request)
        return jsonify(access_token=access_token, refresh_token=refresh_token)


@namespace.route('/logout')
class LogoutView(Resource):
    @namespace.doc(
        'logout', responses={200: 'Вы вышли из аккаунта', 401: 'Пользователь не авторизован!'},
    )
    @namespace.expect(authorization_parser)
    @error_processing(getLogger('LogoutAPIView.post'))
    @jwt_required()
    def post(self):
        """Выход из пользовательской сессии"""
        jwt = get_jwt()['jti']
        AccountsService.logout(jwt, current_user.id)
        return jsonify(message='Вы вышли из аккаунта')


@namespace.route('/refresh')
class RefreshTokensView(Resource):
    @namespace.doc(
        'refresh',
        response={
            200: 'OK',
            401: 'Пользователь не авторизован или refresh-токен недействительный!',
        },
    )
    @namespace.expect(authorization_parser)
    @error_processing(getLogger('RefreshAPIView.post'))
    @jwt_required(refresh=True)
    def post(self):
        """Получение новой пары токенов в обмен на refresh-токен"""
        refresh_token = get_jwt()['jti']
        account_service = AccountsService(current_user)
        access_token, refresh_token = account_service.refresh_token_pair(refresh_token)
        return jsonify(access_token=access_token, refresh_token=refresh_token)


@namespace.route('/resend')
class ResendConfirmEmailView(Resource):
    @namespace.doc(
        'resend confirm email',
        response={
            200: 'OK',
            208: 'E-mail уже подтвержден.',
            401: 'Пользователь не авторизован или refresh-токен недействительный!',
        },
    )
    @namespace.expect(authorization_parser)
    @error_processing(getLogger('ResendConfirmEmailAPIView.post'))
    @jwt_required()
    def post(self):
        if current_user.confirmed:
            return jsonify(message='E-mail уже подтвержден.'), HTTPStatus.ALREADY_REPORTED

        # Генерация и отправка новой ссылки для подтверждения email
        token = generate_confirmation_token(current_user.email)
        confirm_url = url_for('Account_confirm_email_view', token=token, _external=True)
        payload = {
            'user_id': str(current_user.id),
            'user_email': current_user.email,
            'username': current_user.username,
            'first_name': current_user.first_name,
            'last_name': current_user.last_name,
            'token': token,
            'callback_url': confirm_url,
        }
        send_notification(payload)
        return 'Письмо со ссылкой подтверждения e-mail направлено повторно'
