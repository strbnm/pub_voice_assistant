import logging
from logging import getLogger

from flask import jsonify
from flask_jwt_extended import current_user, get_jwt, jwt_required
from flask_restx import Resource, marshal

from app.api.v1.account import namespace
from app.api.v1.account.parsers import (
    history_request_parser,
    user_password_update_request_parser,
)
from app.api.v1.account.schemes import (
    PasswordArgs,
    account_paginator_response,
    user_history_response,
)
from app.database import session_scope
from app.datastore import user_datastore
from app.errors import APIBadRequestError, ErrorsMessages
from app.models.history import HistoryUserAuth
from app.services.auth import AccountsService
from app.utils import error_processing


logger = logging.getLogger(__name__)


@namespace.route('/user/password')
class UserUpdatePasswordAPIView(Resource):
    @namespace.doc(
        'password',
        responses={201: 'Пароль Успешно изменен.', 400: 'Неверно указан старый пароль.'},
    )
    @namespace.expect(user_password_update_request_parser)
    @error_processing(getLogger('UserUpdatePasswordAPIView.patch'))
    @jwt_required()
    def patch(self):
        """Изменение пароля пользователя."""
        args = PasswordArgs(**user_password_update_request_parser.parse_args())
        if not current_user.check_password(password=args.old_password):
            raise APIBadRequestError(ErrorsMessages.WRONG_OLD_PASSWORD.value)
        with session_scope():
            current_user.password = args.new_password
            user_datastore.commit()
        jwt = get_jwt()['jti']
        AccountsService.logout(jwt, current_user.id)
        return jsonify(message='Пароль Успешно изменен.')


@namespace.route('/user/history')
class UserHistoryAPIView(Resource):
    @namespace.doc(
        'history', responses={200: 'Успешная операция', 401: 'Пользователь не авторизован!'},
    )
    @namespace.expect(history_request_parser)
    @namespace.marshal_with(account_paginator_response)
    @error_processing(getLogger('UserHistoryAPIView.get'))
    @jwt_required()
    def get(self):
        """Просмотр истории входов."""
        args = history_request_parser.parse_args()
        queryset = HistoryUserAuth.query.filter_by(user_id=current_user.id).order_by(
            HistoryUserAuth.timestamp.asc()
        )
        paginator = queryset.paginate(
            page=args['page'], per_page=args['per_page'], error_out=False
        )
        logger.debug('Пагинатор: %s', paginator)
        count = paginator.total
        total_pages = paginator.pages
        prev_page = paginator.prev_num if paginator.has_prev else None
        next_page = paginator.next_num if paginator.has_next else None
        logger.debug(
            'Параметры ответа history: count - %s, total_pages - %s, items - %s',
            count,
            total_pages,
            paginator.items,
        )
        return {
            'count': count,
            'total_pages': total_pages,
            'prev': prev_page,
            'next': next_page,
            'results': marshal(paginator.items, user_history_response),
        }
