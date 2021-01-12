from marshmallow import Schema, fields, post_dump, validate, validates, ValidationError

class CommentSchema(Schema):
    class Meta:
        ordered = True

    author = fields.String(validate=[validate.Length(max=100)])
    text = fields.String(validate=[validate.Length(max=500)])
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
