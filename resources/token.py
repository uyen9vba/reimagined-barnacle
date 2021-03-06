from http import HTTPStatus
from flask import request, make_response, render_template, session
from flask_restful import Resource
from flask_jwt_extended import (create_access_token, create_refresh_token,
jwt_refresh_token_required, get_jwt_identity, jwt_required, get_raw_jwt, get_jwt_claims)

from utils import check_password
from models.user import User

black_list = set()

class TokenResource(Resource):
    def post(self):
        json_data = request.get_json()
        email = json_data.get('email')
        password = json_data.get('password')

        user = User.get_by_email(email=email)

        if not user or not check_password(password, user.password):
            return {'message': 'email or password is incorrect'}, HTTPStatus.UNAUTHORIZED

        if user.is_active is False:
            return {'message': 'The user account is not activated yet'}, HTTPStatus.FORBIDDEN

        access_token = create_access_token(identity=user.username, fresh=True)
        refresh_token = create_refresh_token(identity=user.username)

        session['access_token'] = access_token
        session['refresh_token'] = refresh_token

        return {'access_token': access_token, 'refresh_token': refresh_token}, HTTPStatus.OK

class RefreshResource(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()

        token = create_access_token(identity=current_user, fresh=False)

        return {'token': token}, HTTPStatus.OK

class RevokeResource(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']

        black_list.add(jti)

        session['access_token'] = None

        return
