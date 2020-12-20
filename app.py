from flask import Flask, render_template, session, redirect, url_for, request, Response, flash, send_from_directory
from flask_migrate import Migrate
from http import HTTPStatus
from flask_restful import Api
from flask_uploads import configure_uploads, patch_request_class, extension
from flask_jwt_extended import get_jwt_identity, get_jwt_claims, jwt_required
from markupsafe import escape
import requests
import json
import os
import uuid
from config import Config
from extensions import db, jwt, image_set
from models.image import Image
from models.user import User
from resources.image import ImageListResource, ImageResource, ImagePublishResource, ImageCoverUploadResource
from resources.user import UserListResource, UserResource, MeResource, UserImageListResource, UserActivateResource, UserAvatarUploadResource
from resources.token import TokenResource, RefreshResource, RevokeResource, black_list

from resources.tag import TagResource, TagListResource
from models.tag import Tag
from utils import save_image

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

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'GET':
            return render_template('signup.html')
        elif request.method == 'POST':
            requests.post(
                    url='http://localhost:5000/users',
                    json={
                        'email': request.form['email'],
                        'username': request.form['username'],
                        'password': request.form['password']}
                    )
            return redirect(url_for('index'))

    @app.route('/signin', methods=['GET'])
    def signin():
        if request.method == 'GET':
            return render_template('signin.html')
        elif request.method == 'POST':
            session['email'] = request.form['email']
            session['password'] = request.form['password']

            r = requests.post(
                    url='http://localhost:5000/token',
                    json={
                        'email': request.form['email'],
                        'password': request.form['password']}
                    )
            json = r.json()

            return redirect(url_for('index'))
    
    @app.route('/upload', methods=['GET'])
    def upload():
        if request.method == 'GET':
            return render_template('upload.html')
        elif request.method == 'POST':
            if 'file' not in request.files:
                print('No files')

                return redirect(request.url)

            file = request.files['file']

            if file.filename == '':
                print('No selected file')

                return redirect(request.url)

            filename = f'{uuid.uuid4()}.{extension(file.filename)}'

            claims = get_jwt_claims()
            print(claims)

            response = requests.post(
                    url='http://localhost:5000/images',
                    headers={'Authorization': 'Bearer ' + claims['access_token']},
                    json={
                        'name': request.form['name'],
                        'description': request.form['description'],
                        'filename': filename}
                    )
            file.save(os.path.join('static/images/pictures', filename))

        return redirect(url_for('index'))
        
    @app.route('/gallery')
    def get_gallery():
        image_names = os.listdir('./static/images/pictures')
        image_pages = []

        for a in image_names:
            name = os.path.splitext(a)
            image_pages.append(name[0])

        return render_template("gallery.html", image_names=image_names, image_pages=image_pages)

    @app.route('/revoke')
    def singout():
        print('Signing out')
        requests.post(
                url='http://localhost:5000/revoke',
                headers={'Authorization': 'Bearer ' + session['access_token']})

        session['access_token'] = ''

        return redirect(url_for('index'))

    @app.route('/<image>', methods=['GET'])
    def image(image):
        if request.method == 'GET':
            return render_template(f'{image}.html')
        elif request.method == 'DELETE':
            response = requests.delete(
                    url=request.url,
                    headers={'Authorization': 'Bearer ' + session['access_token']})

            return url_for('index')


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
    api.add_resource(UserResource, '/users/<string:username>')
    api.add_resource(UserImageListResource, '/users/<string:username>/images')
    api.add_resource(ImageListResource, '/images')
    api.add_resource(ImageResource, '/images/<string:uuid>')
    api.add_resource(ImagePublishResource, '/images/<int:image_id>/publish')


if __name__ == '__main__':
    app = create_app()
    app.run()

