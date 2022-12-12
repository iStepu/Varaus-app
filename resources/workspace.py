from flask import request
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError
from http import HTTPStatus

from models.workspace import Workspace
from schemas.workspace import WorkspaceSchema

workspace_schema = WorkspaceSchema()
workspace_list_schema = WorkspaceSchema(many=True)


class WorkspaceListResource(Resource):

    @staticmethod
    def post():
        json_data = request.get_json()

        try:
            data = workspace_schema.load(data=json_data)
        except ValidationError as err:
            errors = err.messages
            return {'message': 'Validation errors', 'errors': errors}, HTTPStatus.BAD_REQUEST

        if Workspace.get_by_workspace_id(data.get('username')):
            return {'message': 'id already used'}, HTTPStatus.BAD_REQUEST

        if Workspace.get_by_name(data.get('name')):
            return {'message': 'name already used'}, HTTPStatus.BAD_REQUEST

        workspace = Workspace(**data)
        workspace.save()

        return workspace_schema.dump(workspace), HTTPStatus.CREATED


class WorkspaceResource(Resource):

    @jwt_required(optional=True)
    def get(self, workspace_id):
        workspace = Workspace.get_by_workspace_id(workspace_id=workspace_id)

        if workspace is None:
            return {'message': 'workspace not found'}, HTTPStatus.NOT_FOUND

        return workspace.data, HTTPStatus.OK
