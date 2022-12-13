from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from http import HTTPStatus

from models.user import User
from models.workspace import Workspace
from schemas.workspace import WorkspaceSchema

workspace_schema = WorkspaceSchema()
workspace_list_schema = WorkspaceSchema(many=True)


class WorkspaceListResource(Resource):

    @staticmethod
    def get():
        workspaces = Workspace.get_all()
        return workspace_list_schema.dump(workspaces), HTTPStatus.OK

    @staticmethod
    def post():
        json_data = request.get_json()

        try:
            data = workspace_schema.load(data=json_data)
        except ValidationError as err:
            errors = err.messages
            return {'message': 'Validation errors', 'errors': errors}, HTTPStatus.BAD_REQUEST

        if Workspace.get_by_workspace_id(data.get('id')):
            return {'message': 'id already used'}, HTTPStatus.BAD_REQUEST

        if Workspace.get_by_name(data.get('name')):
            return {'message': 'name already used'}, HTTPStatus.BAD_REQUEST

        workspace = Workspace(**data)
        workspace.save()

        return workspace_schema.dump(workspace), HTTPStatus.CREATED


class WorkspaceResource(Resource):

    @jwt_required(optional=True)
    def get(self, workspace_id):
        workspace = Workspace.get_by_workspace_id(id=workspace_id)

        if workspace is None:
            return {'message': 'workspace not found'}, HTTPStatus.NOT_FOUND

        data = workspace_schema.dump(workspace)

        return data, HTTPStatus.OK

    @jwt_required()
    def patch(self, workspace_id):
        json_data = request.get_json()

        try:
            data = workspace_schema.load(data=json_data, partial=True)
        except ValidationError as err:
            errors = err.messages
            return {'message': 'Validation errors', 'errors': errors}, HTTPStatus.BAD_REQUEST

        workspace = Workspace.get_by_workspace_id(workspace_id)

        if workspace is None:
            return {'message': 'Workspace not found'}, HTTPStatus.NOT_FOUND

        current_user = User.get_by_id(get_jwt_identity())

        if not current_user.is_admin:
            return {'message': 'Access is not allowed, current user is not admin'}, HTTPStatus.FORBIDDEN

        workspace.name = data.get('name') or workspace.name
        workspace.campus = data.get('campus') or workspace.campus
        workspace.building = data.get('building') or workspace.building
        workspace.description = data.get('description') or workspace.description

        workspace.save()

        return workspace_schema.dump(workspace), HTTPStatus.OK

    @jwt_required()
    def delete(self, workspace_id):
        workspace = Workspace.get_by_workspace_id(workspace_id)

        if not workspace:
            return {"message": "workspace not found"}, HTTPStatus.NOT_FOUND

        current_user = User.get_by_id(get_jwt_identity())

        if not current_user.is_admin:
            return {'message': 'Access is not allowed, current user is not admin'}, HTTPStatus.FORBIDDEN

        workspace.delete()

        return {}, HTTPStatus.NO_CONTENT