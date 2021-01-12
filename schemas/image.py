from marshmallow import Schema, fields, post_dump, validate, validates, ValidationError
from flask import url_for

class ImageSchema(Schema):
    class Meta:
        ordered = True

    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=[validate.Length(max=100)])
    description = fields.String(validate=[validate.Length(max=200)])
    uuid = fields.String(validate=[validate.Length(max=200)])
    filename = fields.String(validate=[validate.Length(max=200)])
    private = fields.Boolean()
    cover_url = fields.Method(serialize='dump_cover_url')
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    author = fields.String(validate=[validate.Length(max=100)])
    tags = fields.List(fields.String(validate=[validate.Length(max=100)]))

    @post_dump(pass_many=True)
    def wrap(self, data, many, **kwargs):
        if many:
            return {'data': data}

        return data

    def dump_cover_url(self, image):
        if image.cover_image:
            return url_for('static', filename='images/images/{}'.format(image.cover_image), _external=True)
        else:
            return url_for('static', filename='images/assets/default-image-cover.jpg', _external=True)
