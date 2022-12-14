from marshmallow import Schema, fields, post_dump, validate, validates, ValidationError

from schemas.user import UserSchema
from schemas.workspace import WorkspaceSchema


class ReservationSchema(Schema):
    class Meta:
        ordered = True

    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(dump_only=True)
    workspace_id = fields.Integer(required=True)

    start_date = fields.DateTime(required=True)
    end_date = fields.DateTime(required=True)

    author = fields.Nested(UserSchema, attribute='user', dump_only=True, only=['id', 'username'])
    workspace = fields.Nested(WorkspaceSchema, attribute='workspace', dump_only=True,
                              exclude={'created_at', 'updated_at'})

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @post_dump(pass_many=True)
    def wrap(self, data, many, **kwargs):
        if many:
            return {'data': data}
        return data