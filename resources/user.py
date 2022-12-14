from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from marshmallow import ValidationError
from http import HTTPStatus

from models.user import User
from schemas.user import UserSchema

user_schema = UserSchema()
user_public_schema = UserSchema(exclude=('email', ))
user_list_schema = UserSchema(many=True, exclude=('email', ))


class UserListResource(Resource):

    @staticmethod
    def get():
        users = User.get_all()
        return user_list_schema.dump(users), HTTPStatus.OK

    @staticmethod
    def post():
        json_data = request.get_json()

        try:
            data = user_schema.load(data=json_data)
        except ValidationError as err:
            errors = err.messages
            return {'message': 'Validation errors', 'errors': errors}, HTTPStatus.BAD_REQUEST

        if User.get_by_username(data.get('username')):
            return {'message': 'username already used'}, HTTPStatus.BAD_REQUEST

        if User.get_by_email(data.get('email')):
            return {'message': 'email already used'}, HTTPStatus.BAD_REQUEST

        user = User(**data)
        user.save()

        return user_schema.dump(user), HTTPStatus.CREATED


class UserResource(Resource):

    @jwt_required(optional=True)
    def get(self, username):
        user = User.get_by_username(username=username)

        if user is None:
            return {'message': 'user not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user == user.id:
            data = user_schema.dump(user)
        else:
            data = user_public_schema.dump(user)

        return data, HTTPStatus.OK

    @jwt_required()
    def patch(self, username):
        json_data = request.get_json()

        try:
            data = user_schema.load(data=json_data, partial=True)
        except ValidationError as err:
            errors = err.messages
            return {'message': 'Validation errors', 'errors': errors}, HTTPStatus.BAD_REQUEST

        user = User.get_by_username(username=username)

        if user is None:
            return {'message': 'User not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != user.id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        user.username = data.get('username') or user.username
        user.name = data.get('name') or user.name
        user.email = data.get('email') or user.email
        user.password = data.get('password') or user.password

        user.save()

        return user_schema.dump(user), HTTPStatus.OK

    @jwt_required()
    def delete(self, username):
        user = User.get_by_username(username=username)

        if not user:
            return {"message": "User not found"}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != user.id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        user.delete()

        return {}, HTTPStatus.NO_CONTENT


class MeResource(Resource):

    @jwt_required()
    def get(self):
        user = User.get_by_id(id=get_jwt_identity())
        return user_schema.dump(user), HTTPStatus.OK


class UserAdminRightsResource(Resource):

    @staticmethod
    def put(username):
        user = User.get_by_username(username)

        if not user:
            return {"message": "user not found"}, HTTPStatus.NOT_FOUND

        user.is_admin = True

        user.save()

        return {}, HTTPStatus.NO_CONTENT

    @staticmethod
    def delete(username):
        user = User.get_by_username(username)

        if not user:
            return {"message": "user not found"}, HTTPStatus.NOT_FOUND

        user.is_admin = False

        user.save()

        return {}, HTTPStatus.NO_CONTENT
