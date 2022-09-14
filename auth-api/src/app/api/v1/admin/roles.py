import http
from http import HTTPStatus
from logging import getLogger

from flask_jwt_extended import jwt_required
from flask_restx import Resource, marshal

from app.api.v1.admin import roles_namespace
from app.api.v1.admin.parsers import (
    authorization_parser,
    pagination_request_parser,
    role_request_create_parser,
    role_request_update_parser,
)
from app.api.v1.admin.schemes import RoleItem, roles_paginator_response, roles_role_schema
from app.api.v1.base_view import BaseView
from app.database import session_scope
from app.datastore import user_datastore
from app.errors import APIBadRequestError, APIConflictError, ErrorsMessages
from app.models.roles import Role
from app.utils import error_processing, roles_accepted, roles_required


@roles_namespace.route('/')
class RoleView(Resource, BaseView):
    @roles_namespace.doc(
        'view roles',
        response={200: 'Успешная операция', 403: 'Недостаточно прав. Доступ запрещен.'},
    )
    @roles_namespace.expect(pagination_request_parser)
    @roles_namespace.marshal_with(roles_paginator_response)
    @error_processing(getLogger('RoleView.get'))
    @roles_accepted('staff', 'superuser')
    @jwt_required()
    def get(self):
        """Просмотр ролей."""
        args = pagination_request_parser.parse_args()
        queryset = Role.query.order_by(Role.name.asc())
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
            'results': marshal(paginator.items, roles_role_schema),
        }

    @roles_namespace.doc(
        'create role',
        response={
            201: 'Роль создана',
            400: 'Отсутствует обязательное поле',
            403: 'Недостаточно прав или системная роль. Доступ запрещен.',
            409: 'Роль с таким именем уже существует!',
        },
    )
    @roles_namespace.expect(role_request_create_parser)
    @roles_namespace.marshal_with(roles_role_schema)
    @error_processing(getLogger('RoleView.post'))
    @roles_required('superuser')
    @jwt_required()
    def post(self):
        """Создание ролей."""
        args = RoleItem(**role_request_create_parser.parse_args())
        if not (args.name and args.description):
            raise APIBadRequestError
        role = self.get_object_by_query(Role, check=False, name=args.name)
        if role:
            raise APIConflictError(ErrorsMessages.ROLE_IS_EXIST.value)
        with session_scope():
            new_role = user_datastore.create_role(name=args.name, description=args.description)
            new_role.is_active = True
            user_datastore.commit()
        return new_role, HTTPStatus.CREATED


@roles_namespace.route('/<uuid:role_id>')
class RoleChangeView(Resource, BaseView):
    @roles_namespace.doc(
        'update role',
        response={
            201: 'Успешная операция',
            403: 'Недостаточно прав или системная роль. Доступ запрещен.',
            404: 'Отказано! Роль не может быть удалена!',
            409: 'Роль с таким именем уже существует!',
        },
    )
    @roles_namespace.expect(role_request_update_parser)
    @roles_namespace.marshal_with(roles_role_schema)
    @error_processing(getLogger('RoleChangeView.put'))
    @roles_required('superuser')
    @jwt_required()
    def put(self, role_id):
        """Изменение роли."""
        args = RoleItem(**role_request_update_parser.parse_args())
        if not args:
            raise APIBadRequestError(ErrorsMessages.NOTHING_TO_CHANGE.value)
        role = self.get_object_by_query(Role, id=role_id)
        if role.name in Role.Meta.PROTECTED_ROLE_NAMES:
            raise APIConflictError(ErrorsMessages.UNABLE_TO_CHANGE_BASE_ROLE_VALUE.value)
        with session_scope():
            role.name = args.name if args.name else role.name
            role.description = args.description if args.description else role.description
            user_datastore.commit()
        return role, HTTPStatus.CREATED

    @roles_namespace.doc(
        'delete role',
        response={
            204: '',
            403: 'Недостаточно прав или системная роль. Доступ запрещен.',
            404: 'Роль не найдена',
        },
    )
    @roles_namespace.expect(authorization_parser)
    @error_processing(getLogger('RoleChangeView.delete'))
    @roles_required('superuser')
    @jwt_required()
    def delete(self, role_id):
        """Удаление роли."""
        role = self.get_object_by_query(Role, id=role_id)
        if role.name in Role.Meta.PROTECTED_ROLE_NAMES:
            raise APIConflictError(ErrorsMessages.UNABLE_TO_DELETE_BASE_ROLE_VALUE.value)
        with session_scope() as session:
            session.delete(role)
            user_datastore.commit()
        return {}, http.HTTPStatus.NO_CONTENT
