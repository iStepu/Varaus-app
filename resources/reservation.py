from flask import request
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity, jwt_required
from http import HTTPStatus

from models.reservation import Reservation
from models.workspace import Workspace
from schemas.reservation import ReservationSchema

from marshmallow import ValidationError

reservation_schema = ReservationSchema()
reservation_list_schema = ReservationSchema(many=True)


class ReservationListResource(Resource):

    @staticmethod
    def get():
        reservations = Reservation.get_all()
        return reservation_list_schema.dump(reservations), HTTPStatus.OK

    @jwt_required()
    def post(self):
        json_data = request.get_json()
        current_user = get_jwt_identity()

        try:
            data = reservation_schema.load(data=json_data)
        except ValidationError as err:
            errors = err.messages
            return {'message': 'Validation errors', 'errors': errors}, HTTPStatus.BAD_REQUEST

        if not Workspace.get_by_workspace_id(data.get("workspace_id")):
            return {'message': 'Workspace does not exist'}, HTTPStatus.BAD_REQUEST

        overlapping_reservations = Reservation.get_by_workspace_and_timeslot(
            data["workspace_id"], data["start_date"], data["end_date"])

        if overlapping_reservations:
            return {'message': 'Timeslot not available'}, HTTPStatus.BAD_REQUEST

        reservation = Reservation(**data)
        reservation.user_id = current_user
        reservation.save()

        return reservation_schema.dump(reservation), HTTPStatus.CREATED


class ReservationResource(Resource):

    @staticmethod
    def get(reservation_id):

        reservation = Reservation.get_by_id(reservation_id)

        if reservation is None:
            return {'message': 'reservation not found'}, HTTPStatus.NOT_FOUND

        data = reservation_schema.dump(reservation)

        return data, HTTPStatus.OK

    @jwt_required()
    def delete(self, reservation_id):
        reservation = Reservation.get_by_id(reservation_id)

        if reservation is None:
            return {'message': 'reservation not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != reservation.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        reservation.delete()

        return {}, HTTPStatus.NO_CONTENT
