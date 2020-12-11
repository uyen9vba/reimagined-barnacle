from flask import Flask, render_template, session, redirect, url_for, request, Response, flash
from flask_migrate import Migrate
from flask_restful import Api
from flask_uploads import configure_uploads, patch_request_class
from markupsafe import escape
import requests
import json

from config import Config
from extensions import db, jwt, image_set
from models.user import User
from resources.image import ImageListResource, ImageResource, ImagePublishResource, ImageCoverUploadResource
from resources.user import UserListResource, UserResource, MeResource, UserImageListResource, UserActivateResource, UserAvatarUploadResource
from resources.token import TokenResource, RefreshResource, RevokeResource, black_list

token = None

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

def register_resources(app):
    api = Api(app)

    @app.route('/')
    def index():
        if 'email' in session:
            pass

        return render_template('index.html')

    @app.route('/signup', methods=['POST'])
    def signup():
        render_template('signup.html')

        if request.method == 'POST':
            requests.post(
                    url='http://localhost:5000/users',
                    json={
                        'email': request.form['email'],
                        'username': request.form['username'],
                        'password': request.form['password']}
                    )
            return redirect(url_for('index'))

    @app.route('/signin', methods=['POST'])
    def signin():
        render_template('signin.html')

        if request.method == 'POST':
            session['email'] = request.form['email']
            session['password'] = request.form['password']

            response = requests.post(
                    url='http://localhost:5000/token',
                    json={
                        'email': request.form['email'],
                        'password': request.form['password']}
                    )

            print(response.json)

            token = response.json

            return redirect(url_for('index'))

    @app.route('/upload', methods=['POST', 'PUT'])
    def upload():
        render_template('upload.html')

        if request.method == 'POST':
            if 'file' not in request.files:
                flash('No files')

                return redirect(request.url)

            file = request.files['file']

            if file.filename == '':
                flash('No selected file')

                return redirect(request.url)

            requests.post(
                    url='http://localhost:5000/images',
                    json={
                        'name': request.form['name'],
                        'description': request.form['description']}
                    )


    @app.route('/<image>')
    def image(image):
        return render_template(f'{image}.html')

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
    api.add_resource(ImageResource, '/images/<int:image_id>')
    api.add_resource(ImagePublishResource, '/images/<int:image_id>/publish')


if __name__ == '__main__':
    app = create_app()
    app.run()

