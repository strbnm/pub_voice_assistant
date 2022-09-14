from logging import getLogger

from flask import jsonify, request, url_for
from flask_restx import Resource

from app.api.v1.account import namespace
from app.errors import APINotFoundError, APIUnauthorizedError, OAuthServiceError
from app.oauth import oauth
from app.services.oauth import OauthService
from app.utils import error_processing, traced


@namespace.route('/login/<string:social_name>')
class OauthLoginAPIView(Resource):
    @namespace.doc(
        'oauth login',
        response={
            404: 'Возможность авторизации c аккаунтом в этой социальной сети не найдена'
        },
    )
    @traced('OauthLoginAPIView')
    @error_processing(getLogger('OauthLoginAPIView.get'))
    @traced('OauthLoginAPIView')
    def get(self, social_name: str):
        client = oauth.create_client(social_name)
        if not client:
            raise APINotFoundError

        redirect_url = url_for(
            'Account_oauth_authorization_api_view', social_name=social_name, _external=True
        )

        return client.authorize_redirect(redirect_url)


@namespace.route('/auth/<string:social_name>')
class OauthAuthorizationAPIView(Resource):
    @namespace.doc(
        'oauth authorization',
        response={
            200: 'Успешная операция',
            403: 'Пользователь не авторизован!',
            404: 'Возможность авторизации c аккаунтом в этой социальной сети не найдена',
        },
    )
    @traced('OauthAuthorizationAPIView')
    @error_processing(getLogger('OauthLoginAPIView.get'))
    def get(self, social_name: str):
        client = oauth.create_client(social_name)
        if not client:
            raise APINotFoundError

        token = client.authorize_access_token()
        user_info = token.get('userinfo')

        if not user_info:
            user_info = client.userinfo()

        oauth_service = OauthService(
            social_name=social_name,
            social_id=user_info['sub'],
            user_name=user_info['name'],
            user_email=user_info['email'],
        )

        try:
            access_token, refresh_token = oauth_service.login(request)
        except OAuthServiceError:
            raise APIUnauthorizedError

        return jsonify(access_token=access_token, refresh_token=refresh_token)
