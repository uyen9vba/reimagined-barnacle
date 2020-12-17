from flask import request
from flask_restful import Resource
from http import HTTPStatus
from flask_jwt_extended import get_jwt_identity, jwt_required, jwt_optional

from models.tag import Tag
from schemas.tag import TagSchema
import os

tag_schema = TagSchema()
tag_list_schema = TagSchema(many=True)


class TagListResource(Resource):
    def get(self):
        tags = Tag.get_all()

        return tag_list_schema.dump(tags).data, HTTPStatus.OK

    @jwt_required
    def post(self):
        json_data = request.get_json()

        name = json_data['name']

        data, errors = tag_schema.load(data=json_data)

        if errors:
            return {'message': 'Validation errors', 'errors': errors}, HTTPStatus.BAD_REQUEST

        current_user = get_jwt_identity()
        tag = Tag(**data)
        tag.user_id = current_user
        tag.save()


        return tag_schema.dump(tag).data, HTTPStatus.CREATED


class TagResource(Resource):
    @jwt_optional
    def get(self, tag_id):
        tag = Tag.get_by_id(tag_id=tag_id)

        if tag is None:
            return {'message': 'tag not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if tag.user_id != current_user:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        return tag_schema.dump(tag).data, HTTPStatus.OK

    @jwt_required
    def patch(self, tag_id):
        json_data = request.get_json()

        data, errors = tag_schema.load(data=json_data, partial=('name',))

        if errors:
            return {'message': 'Validation errors', 'errors': errors}, HTTPStatus.BAD_REQUEST

        tag = Tag.get_by_id(tag_id=tag_id)

        if tag is None:
            return {'message': 'Tag not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != tag.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        tag.name = data.get('name') or tag.name

        tag.save()

        return tag_schema.dump(tag).data, HTTPStatus.OK

    @jwt_required
    def delete(self, tag_id):
        tag = Tag.get_by_id(tag_id=tag_id)

        if tag is None:
            return {'message': 'Tag not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != tag.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        tag.delete()

        return {}, HTTPStatus.NO_CONTENT

