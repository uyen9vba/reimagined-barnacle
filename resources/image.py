from flask import request, session, render_template, make_response
from flask_restful import Resource
from flask_uploads import extension
from http import HTTPStatus
from flask_jwt_extended import get_jwt_identity, jwt_required, jwt_optional
import jinja2

from models.image import Image
from schemas.image import ImageSchema

import os
from extensions import image_set
from utils import save_image


image_schema = ImageSchema()
image_list_schema = ImageSchema(many=True)
image_cover_schema = ImageSchema(only=('cover_url', ))


class ImageListResource(Resource):
    def post(self):
        name = request.form.get('name')
        description = request.form.get('description')
        file = request.files['file']
        filename = save_image(image=file, folder='images')
        filename = os.path.splitext(filename)

        data, errors = image_schema.load({
            'name': name,
            'description': description,
            'uuid': filename[0],
            'filename': filename[0] + filename[1]})
        
        if errors:
            return {'message': 'Validation errors', 'errors': errors}, HTTPStatus.BAD_REQUEST

        image = Image(**data)

        current_user = get_jwt_identity()

        if not file:
            return {'message': 'Not a valid image'}, HTTPStatus.BAD_REQUEST

        if not image_set.file_allowed(file, file.filename):
            return {'message': 'File type not allowed'}, HTTPStatus.BAD_REQUEST

        image.user_id = current_user
        image.save()

        return image_schema.dump(image).data, HTTPStatus.CREATED

class ImageResource(Resource):
    @jwt_optional
    def get(self, uuid):
        image = Image.get_by_uuid(uuid)

        if image is None:
            return {'message': 'image not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if image.is_publish == False and image.user_id != current_user:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        return make_response(render_template(
                '/imagecontent.html',
                name=image.name,
                filename=image.filename,
                description=image.description))

    def patch(self, uuid):
        json_data = request.get_json()
        print(json_data)

        data, errors = image_schema.load(data=json_data, partial=('name',))

        if errors:
            return {'message': 'Validation errors', 'errors': errors}, HTTPStatus.BAD_REQUEST

        image = Image.get_by_uuid(uuid)

        if image is None:
            return {'message': 'Image not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != image.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        image.name = data.get('name') or image.name
        image.description = data.get('description') or image.description

        image.save()

        return image_schema.dump(image).data, HTTPStatus.OK

    def delete(self, uuid):
        image = Image.get_by_uuid(uuid)

        if image is None:
            return {'message': 'Image not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != image.user_id:
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

        if current_user != image.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        image.is_publish = True
        image.save()

        return {}, HTTPStatus.NO_CONTENT


    def delete(self, image_id):

        image = Image.get_by_id(image_id=image_id)

        if image is None:
            return {'message': 'image not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != image.user_id:
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

        if current_user != image.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        if image.cover_image:
            cover_path = image_set.path(folder='images', filename=image.cover_image)
            if os.path.exists(cover_path):
                os.remove(cover_path)

        filename = save_image(image=file, folder='pictures', filename=file.filename)

        image.cover_image = filename
        image.save()

        return image_cover_schema.dump(image).data, HTTPStatus.OK


