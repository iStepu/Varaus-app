from flask import request
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError
from http import HTTPStatus

from models.workspace import Workspace
from schemas.workspace import WorkspaceSchema

workspace_schema = WorkspaceSchema()
workspace_list_schema = WorkspaceSchema(many=True)


class WorkspaceResource(Resource):

    @jwt_required(optional=True)
    def get(self, workspace_id):
        workspace = Workspace.get_by_workspace_id(workspace_id=workspace_id)

        if workspace is None:
            return {'message': 'workspace not found'}, HTTPStatus.NOT_FOUND

        return workspace.data, HTTPStatus.OK
