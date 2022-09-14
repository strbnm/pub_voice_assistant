from http import HTTPStatus
from logging import getLogger

from flask_jwt_extended import jwt_required
from flask_restx import Resource, marshal

from app.api.v1.admin import users_namespace
from app.api.v1.admin.parsers import (
    authorization_parser,
    pagination_request_parser,
    users_ids_request_parser,
)
from app.api.v1.admin.schemes import (
    users_paginator_response,
    users_role_schema,
    userinfo_response,
)
from app.api.v1.base_view import BaseView
from app.database import session_scope
from app.datastore import user_datastore
from app.errors import APIConflictError, ErrorsMessages
from app.models.roles import Role
from app.models.user import User
from app.utils import error_processing, roles_accepted, roles_required


@users_namespace.route('/<uuid:user_id>/roles')
class UsersRoleAPIView(Resource, BaseView):
    @users_namespace.doc(
        'roles of user',
        response={
            HTTPStatus.OK: 'Успешная операция',
            HTTPStatus.NOT_FOUND: 'Пользователь не найден',
            HTTPStatus.FORBIDDEN: 'Недостаточно прав. Доступ запрещен.',
        },
    )
    @users_namespace.expect(pagination_request_parser)
    @users_namespace.marshal_with(users_paginator_response)
    @error_processing(getLogger('UsersRoleAPIView.get'))
    @roles_accepted('staff', 'superuser')
    @jwt_required()
    def get(self, user_id):
        """Просмотр ролей пользователя"""
        args = pagination_request_parser.parse_args()
        queryset = User.query.filter_by(id=user_id).join(User.roles)
        paginator = queryset.paginate(
            page=args['page'], per_page=args['per_page'], error_out=False
        )
        count = paginator.total
        total_pages = paginator.pages
        prev_page = paginator.prev_num if paginator.has_prev else None
        next_page = paginator.next_num if paginator.has_next else None
        return {
            'count': count,
            'total_pages': total_pages,
            'prev': prev_page,
            'next': next_page,
            'results': marshal([item.roles for item in paginator.items], users_role_schema),
        }


@users_namespace.route('/<uuid:user_id>')
class UserinfoAPIView(Resource, BaseView):
    @users_namespace.doc(
        'get userinfo',
        response={
            HTTPStatus.OK: 'Успешная операция',
            HTTPStatus.NOT_FOUND: 'Пользователь не найден',
            HTTPStatus.FORBIDDEN: 'Недостаточно прав. Доступ запрещен.',
        },
    )
    @users_namespace.expect(authorization_parser)
    @users_namespace.marshal_with(userinfo_response)
    @error_processing(getLogger('UserinfoAPIView.get'))
    @roles_accepted('staff', 'superuser')
    @jwt_required()
    def get(self, user_id):
        """Получение userinfo пользователя"""
        user = User.query.get_or_404(user_id)
        return user, HTTPStatus.OK


@users_namespace.route('/')
class UsersIdsAPIView(Resource, BaseView):
    @users_namespace.doc(
        'get users ids',
        response={
            HTTPStatus.OK: 'Успешная операция',
            HTTPStatus.NOT_FOUND: 'Пользователи не найдены',
            HTTPStatus.FORBIDDEN: 'Недостаточно прав. Доступ запрещен.',
        },
    )
    @users_namespace.expect(users_ids_request_parser)
    @error_processing(getLogger('UsersIdsAPIView.get'))
    @roles_accepted('staff', 'superuser')
    @jwt_required()
    def get(self):
        """Получение userinfo пользователя"""
        args = users_ids_request_parser.parse_args()
        if not args['roles']:
            users = None
            if 'active' in args['status']:
                users = User.query.filter_by(active=True).all()
            elif 'all' in args['status']:
                users = User.query.all()
            if not users:
                return 'Пользователи не найдены', HTTPStatus.NOT_FOUND
            users_ids = [str(user.id) for user in users]
            return {'users_ids': users_ids}, HTTPStatus.OK
        roles = Role.query.all()
        users = User.query.join(User.roles).filter(
            Role.id.in_(role.id for role in roles if role.name in args['roles'])
        )
        if not users:
            return 'Пользователи не найдены', HTTPStatus.NOT_FOUND
        users_ids = [str(user.id) for user in users]
        return {'users_ids': users_ids}, HTTPStatus.OK


@users_namespace.route('/<uuid:user_id>/roles/<uuid:role_id>')
class UsersRoleChangeAPIView(Resource, BaseView):
    @users_namespace.doc(
        'add the role to the user',
        response={
            201: 'Успешная операция',
            204: 'Такая роль уже есть у пользователя',
            404: 'Роль или пользователь не найдены',
            403: 'Недостаточно прав. Доступ запрещен.',
        },
    )
    @users_namespace.expect(authorization_parser)
    @error_processing(getLogger('UsersRoleChangeAPIView.put'))
    @roles_required('superuser')
    @jwt_required()
    def put(self, user_id, role_id):
        """Назначить пользователю роль (добавить в группу роли)"""
        user = User.query.get_or_404(user_id)
        role = Role.query.get_or_404(role_id)
        if role in user.roles:
            raise APIConflictError(ErrorsMessages.ROLE_IS_EXIST_TO_USER.value.format(role))
        with session_scope():
            user_datastore.add_role_to_user(user, role)
        return {}, HTTPStatus.CREATED

    @users_namespace.doc(
        'remove the role from the user',
        response={
            204: '',
            404: 'Роль или пользователь не найдены',
            403: 'Недостаточно прав. Доступ запрещен.',
        },
    )
    @users_namespace.expect(authorization_parser)
    @roles_required('superuser')
    @jwt_required()
    @error_processing(getLogger('UsersRoleChangeAPIView.delete'))
    def delete(self, user_id, role_id):
        """Аннулировать пользователю роль (удалить из группы роли)"""
        user = User.query.get_or_404(user_id)
        role = Role.query.get_or_404(role_id)
        with session_scope():
            user_datastore.remove_role_from_user(user, role)
        return {}, HTTPStatus.NO_CONTENT
