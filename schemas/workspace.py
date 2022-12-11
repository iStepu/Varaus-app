from marshmallow import Schema, fields


class WorkspaceSchema(Schema):
    class Meta:
        ordered = True

    id = fields.Int(dump_only=True)
    name = fields.String(required=True)
    campus = fields.String(required=True)
    building = fields.String(required=True)
    description = fields.String(required=True)

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
