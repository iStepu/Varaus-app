from flask import request
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity, jwt_required
from http import HTTPStatus

from models.reservation import Reservation
from schemas.reservation import ReservationSchema

from marshmallow import ValidationError

reservation_schema = ReservationSchema()
reservation_list_schema = ReservationSchema(many=True)


class ReservationListResource(Resource):

    @jwt_required()
    def post(self):
        json_data = request.get_json()
        current_user = get_jwt_identity()

        try:
            data = reservation_schema.load(data=json_data)
        except ValidationError as err:
            errors = err.messages
            return {'message': 'Validation errors', 'errors': errors}, HTTPStatus.BAD_REQUEST

        reservation = Reservation(**data)
        reservation.user_id = current_user
        reservation.save()

        return reservation_schema.dump(reservation), HTTPStatus.CREATED


class ReservationResource(Resource):

    @jwt_required(optional=True)
    def get(self, reservation_id):

        reservation = Reservation.get_by_id(reservation_id=reservation_id)

        if reservation is None:
            return {'message': 'reservation not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

    @jwt_required()
    def patch(self, reservation_id):

        json_data = request.get_json()

        try:
            data = reservation_schema.load(data=json_data)
        except ValidationError as err:
            errors = err.messages
            return {'message': 'Validation errors', 'errors': errors}, HTTPStatus.BAD_REQUEST

        reservation = Reservation.get_by_id(reservation_id=reservation_id)

        if reservation is None:
            return {'message': 'Reservation not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != reservation.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        reservation.user_id = data.get('user_id') or reservation.user_id
        reservation.workspace_id = data.get('workspace_id') or reservation.workspace_id
        reservation.date = data.get('date') or reservation.date

        reservation.save()

        return reservation.dump(reservation), HTTPStatus.OK

    @jwt_required()
    def put(self, reservation_id):

        json_data = request.get_json()

        reservation = Reservation.get_by_id(reservation_id=reservation_id)

        if reservation is None:
            return {'message': 'reservation not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != reservation.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        reservation.user_id = json_data['user_id']
        reservation.workspace_id = json_data['workspace_id']
        reservation.date = json_data['date']

        reservation.save()

        return reservation.data(), HTTPStatus.OK

    @jwt_required()
    def delete(self, reservation_id):
        reservation = Reservation.get_by_id(reservation_id=reservation_id)

        if reservation is None:
            return {'message': 'reservation not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != reservation.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        reservation.delete()

        return {}, HTTPStatus.NO_CONTENT
