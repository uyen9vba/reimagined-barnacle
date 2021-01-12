from flask import Flask, render_template, session, redirect, url_for, request, Response, flash, send_from_directory
from flask_migrate import Migrate
from http import HTTPStatus
from flask_restful import Api
from flask_uploads import configure_uploads, patch_request_class, extension
from flask_jwt_extended import get_jwt_identity, get_jwt_claims, jwt_required, decode_token
from markupsafe import escape
import requests
import json
import os
import uuid
from config import Config
from extensions import db, jwt, image_set
from models.image import Image
from schemas.image import ImageSchema
from models.user import User
from resources.image import ImageListResource, ImageResource, ImagePublishResource, ImageCoverUploadResource
from resources.user import UserListResource, UserResource, MeResource, UserImageListResource, UserActivateResource, UserAvatarUploadResource
from resources.token import TokenResource, RefreshResource, RevokeResource, black_list

from resources.tag import TagResource, TagListResource
from models.tag import Tag
from utils import save_image

image_list_schema = ImageSchema(many=True)

def create_app():
    app = Flask(__name__)
    app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
    app.config.from_object(Config)

    register_extensions(app)
    register_resources(app)

    return app

def register_extensions(app):
    db.app = app
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt.init_app(app)
    configure_uploads(app, image_set)
    patch_request_class(app, 10 * 1024 * 1024)

    @jwt.token_in_blacklist_loader
    def check_if_token_in_blacklist(decrypted_token):
        jti = decrypted_token['jti']

        return jti in black_list

    @jwt.user_claims_loader
    def set_token(token):
        return {'access_token': token}

def register_resources(app):
    api = Api(app)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/signup')
    def signup():
        return render_template('signup.html')

    @app.route('/signin')
    def signin():
        return render_template('signin.html')

    @app.route('/upload')
    def upload():
        return render_template('upload.html')

    @app.route('/profile')
    def profile():
        current_user = decode_token(session['access_token']).get('identity', None)

        user = User.get_by_username(username=current_user)

        if user is None:
            return {'message': 'user not found'}, HTTPStatus.NOT_FOUND

        return render_template(
                'profile.html',
                avatar_image=user.avatar_image,
                username=user.username,
                email=user.email)

    @app.route('/images')
    def images():
        if request.args.get('private') == 'true':
            current_user = decode_token(session['access_token']).get('identity', None)

            if current_user:
                images = Image.get_all_by_user(current_user)
            else:
                images = Image.get_all()
        else:
            images = Image.get_all()

        data = image_list_schema.dump(images).data
        json = data['data']

        filenames = []
        uuids = []
        names = []

        for a in json:
            filenames.append(a['filename'])
            uuids.append(a['uuid'])
            names.append(a['name'])

        return render_template(
                "gallery.html",
                filenames=filenames,
                uuids=uuids,
                names=names)
     
    api.add_resource(TagResource, '/tags/<int:tag_id>')
    api.add_resource(TagListResource, '/tags')
    api.add_resource(ImageCoverUploadResource, '/images/<int:image_id>/cover')
    api.add_resource(UserAvatarUploadResource, '/users/avatar')
    api.add_resource(UserActivateResource, '/users/activate/<string:token>')
    api.add_resource(TokenResource, '/token')
    api.add_resource(RefreshResource, '/refresh')
    api.add_resource(RevokeResource, '/revoke')
    api.add_resource(MeResource, '/me')
    api.add_resource(UserListResource, '/users')
    api.add_resource(UserResource, '/user')
    api.add_resource(UserImageListResource, '/users/<string:username>/images')
    api.add_resource(ImageListResource, '/images')
    api.add_resource(ImageResource, '/images/<string:uuid>')
    api.add_resource(ImagePublishResource, '/images/<int:image_id>/publish')


if __name__ == '__main__':
    app = create_app()
    app.run()

