from flask import request
from flask_restful import Resource
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

path_to_templates = 'C:/Users/Jone/Desktop/Working file/templates'

class ImageListResource(Resource):
    def get(self):
        images = Image.get_all_published()

        return image_list_schema.dump(images).data, HTTPStatus.OK

    @jwt_required
    def post(self):
        json_data = request.get_json()

        name = json_data['name']
        description = json_data['description']
        filename = json_data['filename']

        current_user = get_jwt_identity()

        data, errors = image_schema.load(data=json_data)
        
        if errors:
            return {'message': 'Validation errors', 'errors': errors}, HTTPStatus.BAD_REQUEST

        image = Image(**data)
        image.user_id = current_user
        image.save()

        jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))

        jinja_var = {
            'title': name,
            'name' : name,
            'description': description
        }

        template = jinja_env.get_template('imagecontent.html')
        output = template.render(title=jinja_var['name'], name=jinja_var['name'],image=jinja_var['image'],description=jinja_var['description'])

        with open(path_to_templates + "/" + filename + ".html", "w") as fh:
            fh.write(output)

        return image_schema.dump(image).data, HTTPStatus.CREATED

class ImageResource(Resource):
    @jwt_optional
    def get(self, image_id):
        image = Image.get_by_id(image_id=image_id)

        if image is None:
            return {'message': 'image not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if image.is_publish == False and image.user_id != current_user:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        return image_schema.dump(image).data, HTTPStatus.OK

    @jwt_required
    def patch(self, image_id):
        json_data = request.get_json()

        data, errors = image_schema.load(data=json_data, partial=('name',))

        if errors:
            return {'message': 'Validation errors', 'errors': errors}, HTTPStatus.BAD_REQUEST

        image = Image.get_by_id(image_id=image_id)

        if image is None:
            return {'message': 'Image not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != image.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        image.name = data.get('name') or image.name
        image.description = data.get('description') or image.description

        image.save()

        return image_schema.dump(image).data, HTTPStatus.OK


    @jwt_required
    def delete(self, image_id):
        image = Image.get_by_id(image_id=image_id)

        if image is None:
            return {'message': 'Image not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != image.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

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

        filename = save_image(image=file, folder='assets', filename=file.filename)

        image.cover_image = filename
        image.save()

        return image_cover_schema.dump(image).data, HTTPStatus.OK


