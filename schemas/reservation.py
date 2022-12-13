from marshmallow import Schema, fields, post_dump, validate, validates, ValidationError
from schemas.user import UserSchema


class ReservationSchema(Schema):
    class Meta:
        ordered = True

    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(dump_only=True)
    workspace_id = fields.Integer(required=True)

    start_date = fields.DateTime('%d-%m-%YT%H:%M', required=True)
    end_date = fields.DateTime('%d-%m-%YT%H:%M', required=True)

    author = fields.Nested(UserSchema, attribute='user', dump_only=True, only=['id', 'username'])

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @post_dump(pass_many=True)
    def wrap(self, data, many, **kwargs):
        if many:
            return {'data': data}
        return data