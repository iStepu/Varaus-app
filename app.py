from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api

from config import Config
from extensions import db, jwt
from resources.user import UserListResource, UserResource, MeResource
from resources.token import TokenResource, RefreshResource, RevokeResource, block_list
from resources.workspace import WorkspaceResource

# Imported directly to be able to create the tables, can be removed
# later when used in resources.
from models.user import User
from models.workspace import Workspace
from models.reservation import Reservation

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    register_extensions(app)
    register_resources(app)

    return app


def register_extensions(app):
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt.init_app(app)
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        return jti in block_list


def register_resources(app):
    api = Api(app)

    api.add_resource(UserListResource, '/users')
    api.add_resource(UserResource, '/users/<string:username>')
    api.add_resource(MeResource, '/me')
    api.add_resource(TokenResource, '/token')
    api.add_resource(RefreshResource, '/refresh')
    api.add_resource(RevokeResource, '/revoke')
    api.add_resource(WorkspaceResource, '/workspaces')


if __name__ == '__main__':
    app = create_app()
    app.run()
