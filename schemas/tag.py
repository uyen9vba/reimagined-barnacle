from marshmallow import Schema, fields, post_dump, validate, validates, ValidationError
from schemas.user import UserSchema
from flask import url_for

class TagSchema(Schema):
    class Meta:
        ordered = True

    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=[validate.Length(max=100)])

    author = fields.Nested(UserSchema, attribute='user', dump_only=True, only=['id', 'username'])