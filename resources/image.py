from flask import request, session, render_template, make_response
from flask_restful import Resource
from flask_uploads import extension
from http import HTTPStatus
from flask_jwt_extended import get_jwt_identity, jwt_required, jwt_optional, decode_token
import jinja2
import datetime

from models.image import Image
from schemas.image import ImageSchema
from models.user import User
from models.tag import Tag
from schemas.tag import TagSchema

import os
from extensions import image_set
from utils import save_image


image_schema = ImageSchema()
image_list_schema = ImageSchema(many=True)
image_cover_schema = ImageSchema(only=('cover_url', ))
tag_schema = TagSchema()


class ImageListResource(Resource):
    @jwt_required
    def post(self):
        current_user = get_jwt_identity()

        name = request.form.get('name')
        description = request.form.get('description')
        file = request.files['file']
        filename = save_image(image=file, folder='images')
        filename = os.path.splitext(filename)
        private = request.form.get('private')
        form_tags = request.form.get('tags').split(',')
        tags = []

        if not file:
            return {'message': 'Not a valid image'}, HTTPStatus.BAD_REQUEST

        if not image_set.file_allowed(file, file.filename):
            return {'message': 'File type not allowed'}, HTTPStatus.BAD_REQUEST
        
        for a, b in enumerate(form_tags):
            if Tag.get_by_name(form_tags[a]) is None:
                data, errors = tag_schema.load({
                    'author': current_user,
                    'name': form_tags[a]})

                tag = Tag(**data)
                tag.save()

            tags.append(form_tags[a])

        data, errors = image_schema.load({
            'name': name,
            'description': description,
            'uuid': filename[0],
            'private': True if private == 'true' else False,
            'filename': filename[0] + filename[1],
            'author': current_user,
            'tags': tags})

        if errors:
            return {'message': 'Validation errors', 'errors': errors}, HTTPStatus.BAD_REQUEST

        image = Image(**data)
        image.save()

        return image_schema.dump(image).data, HTTPStatus.CREATED

class ImageResource(Resource):
    @jwt_optional
    def get(self, uuid):
        image = Image.get_by_uuid(uuid)
        print(image)

        if image is None:
            return {'message': 'image not found'}, HTTPStatus.NOT_FOUND

        if image.private == True:
            current_user = decode_token(session['access_token']).get('identity', None)

            if image.author != current_user:
                return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        user = User.get_by_username(image.author)

        created_at = datetime.datetime.now() - image.created_at

        if created_at.days > 0:
            if created_at.days == 1:
                time = f'{created_at.days} day'
            else:
                time = f'{created_at.days} days'
        elif created_at.seconds / 60 > 0:
            minutes = created_at.seconds / 60
            time = f'{created_at.seconds / 60}'

            if minutes > 60:
                hours = minutes / 60
                hours = str(hours).split('.')[0]
                if hours == '1':
                    time = f'{hours} hour'
                else:
                    time = f'{hours} hours'
            else:
                time = time.split('.')[0]
                time = f'{time} minutes'
        else:
            time = f'{created_at.total_seconds()}'

        time = time + ' ago'

        return make_response(render_template(
                '/imagecontent.html',
                avatar_image=user.avatar_image,
                author=image.author,
                time=time,
                name=image.name,
                filename=image.filename,
                description=image.description,
                tags=image.tags))

    @jwt_required
    def patch(self, uuid):
        json_data = request.get_json()
        print(json_data)

        data, errors = image_schema.load({
            'name': json_data['name'],
            'description': json_data['description'],
            'private': json_data['private'],
            'tags': json_data['tags']})

        if errors:
            return {'message': 'Validation errors', 'errors': errors}, HTTPStatus.BAD_REQUEST

        image = Image.get_by_uuid(uuid)

        if image is None:
            return {'message': 'Image not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != image.author:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        image.name = data.get('name') or image.name
        image.description = data.get('description') or image.description
        image.private = data.get('private')
        image.tags = data.get('tags')

        image.save()

        return image_schema.dump(image).data, HTTPStatus.OK
    
    @jwt_required
    def delete(self, uuid):
        image = Image.get_by_uuid(uuid)

        if image is None:
            return {'message': 'Image not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()
        print(current_user)

        if current_user != image.author:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        os.remove(os.getcwd() + '/static/images/images/' + image.filename)

        image.delete()

        return {}, HTTPStatus.NO_CONTENT

class ImagePublishResource(Resource):

    @jwt_required
    def put(self, image_id):
        image = Image.get_by_id(image_id=image_id)

        if image is None:
            return {'message': 'image not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != image.author:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        image.is_publish = True
        image.save()

        return {}, HTTPStatus.NO_CONTENT


    def delete(self, image_id):

        image = Image.get_by_id(image_id=image_id)

        if image is None:
            return {'message': 'image not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != image.author:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        image.is_publish = False
        image.save()

        return {}, HTTPStatus.NO_CONTENT


class ImageCoverUploadResource(Resource):
    
    @jwt_required
    def put(self, image_id):

        file = request.files.get('cover')

        if not file:
            return {'message': 'Not a valid image'}, HTTPStatus.BAD_REQUEST

        if not image_set.file_allowed(file, file.filename):
            return {'message': 'File type not allowed'}, HTTPStatus.BAD_REQUEST

        image = Image.get_by_id(image_id=image_id)

        if image is None:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != image.author:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        if image.cover_image:
            cover_path = image_set.path(folder='images', filename=image.cover_image)
            if os.path.exists(cover_path):
                os.remove(cover_path)

        filename = save_image(image=file, folder='pictures', filename=file.filename)

        image.cover_image = filename
        image.save()

        return image_cover_schema.dump(image).data, HTTPStatus.OK


