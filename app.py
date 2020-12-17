from flask import Flask, render_template, session, redirect, url_for, request, Response, flash, send_from_directory
from flask_migrate import Migrate
from http import HTTPStatus
from flask_restful import Api
from flask_uploads import configure_uploads, patch_request_class
from flask_jwt_extended import get_jwt_identity
from markupsafe import escape
import requests
import json
import os
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


    access_token = ""

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
            json = response.json()
            print(json['access_token'])

            session['access_token'] = json['access_token']



            return redirect(url_for('index'))




    @app.route('/upload', methods=['POST', 'PUT'])
    def upload():
        render_template('upload.html')

        if request.method == 'POST':
            if 'file' not in request.files:
                print('No files')

                return redirect(request.url)

            file = request.files['file']
            print(file)

            if file.filename == '':
                print('No selected file')

                return redirect(request.url)

            print(str(session['access_token']))

            response = requests.post(
                    url='http://localhost:5000/images',
                    headers={'Authorization': 'Bearer ' + str(session['access_token'])},
                    json={
                        'name': request.form['name'],
                        'description': request.form['description'],
                        'filename': file.filename}
                    )
            json = response.json()
            print(json)

            file.save(os.path.join('static/images/pictures', file.filename))
            '''
            image_id = json['id']
            files = {'file': open(os.getcwd() + file.filename, 'rb')}

            requests.put(
                    url='http://localhost:5000/' + str(image_id) + '/cover',
                    headers={'Authorization': 'Bearer ' + str(session['access_token'])},
                    files=files
                    )
            '''

        return redirect(url_for('index'))
        
    @app.route('/gallery')
    def get_gallery():
       image_names = os.listdir('./static/images/pictures')
       image_pages = []
       for a in image_names:
           name = os.path.splitext(a)
           image_pages.append(name[0])

       return render_template("gallery.html", image_names=image_names, image_pages=image_pages)


    @app.route('/<image>')
    def image(image):
        return render_template(f'{image}.html')



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
    api.add_resource(ImageResource, '/images/<int:image_id>')
    api.add_resource(ImagePublishResource, '/images/<int:image_id>/publish')


if __name__ == '__main__':
    app = create_app()
    app.run()

