from flask import Flask, render_template
from flask_migrate import Migrate
from flask_restful import Api
from flask_uploads import configure_uploads, patch_request_class

from config import Config
from extensions import db, jwt, image_set
from models.user import User
from resources.image import ImageListResource, ImageResource, ImagePublishResource, ImageCoverUploadResource
from resources.user import UserListResource, UserResource, MeResource, UserImageListResource, UserActivateResource, UserAvatarUploadResource
from resources.token import TokenResource, RefreshResource, RevokeResource, black_list


def create_app():
    app = Flask(__name__)
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
        return render_template('index.html')

    @app.route('/<image>')
    def image(image):
        return render_template(f'{image}.html')

    @app.route('/signup')
    def signup():
        return render_template('signup.html')

    @app.route('/signin')
    def signin():
        return render_template('signin.html')

    @app.route('/upload')
    def upload():
        return render_template('upload.html')

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

