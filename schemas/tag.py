from marshmallow import Schema, fields, post_dump, validate, validates, ValidationError

class TagSchema(Schema):
    class Meta:
        ordered = True

    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=[validate.Length(max=100)])
    author = fields.String(validate=[validate.Length(max=100)])
