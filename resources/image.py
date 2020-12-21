from flask import request, session
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
    def get(self):
        images = Image.get_all()

        return image_list_schema.dump(images).data, HTTPStatus.OK

    def post(self):
        name = request.form.get('name')
        description = request.form.get('description')
        file = request.files['file']
        filename = save_image(image=file, folder='pictures')
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

        jinja_var = {
            'name' : name,
            'description': description,
            'filename': filename[0] + filename[1]
        }

        image.user_id = current_user
        image.save()

        jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))

        template = jinja_env.get_template('imagecontent.html')
        output = template.render(
                name=jinja_var['name'],
                description=jinja_var['description'],
                filename=jinja_var['filename'],
                session=session)

        with open(os.getcwd() + "/templates/" + filename[0] + ".html", "w") as fh:
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

    def patch(self, uuid):
        json_data = request.get_json()

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

        jinja_var = {
            'name' : image.name,
            'description': image.description,
            'filename': image.filename
        }

        jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))

        template = jinja_env.get_template('imagecontent.html')
        output = template.render(
                name=jinja_var['name'],
                description=jinja_var['description'],
                filename=jinja_var['filename'],
                session=session)

        with open(os.getcwd() + "/templates/" + uuid + ".html", "w") as fh:
            fh.write(output)

        image.save()

        return image_schema.dump(image).data, HTTPStatus.OK

    def delete(self, uuid):
        image = Image.get_by_uuid(uuid)

        if image is None:
            return {'message': 'Image not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != image.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        template = os.path.splitext(image.filename)

        os.remove(os.getcwd() + '/static/images/pictures/' + image.filename)
        os.remove(os.getcwd() + '/templates/' + template[0] + ".html")

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


