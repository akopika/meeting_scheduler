from datetime import datetime

from flask import request
from flask_restful import Resource

from meeting_scheduler.src import app_factory
from meeting_scheduler.src.db_service import (
    CRUDService,
    are_participants_have_timeslot,
    dont_have_meeting_overlap,
    dont_have_timeslot_overlap,
    get_user_meetings,
)
from meeting_scheduler.src.models import Meeting, Timeslot, User
from meeting_scheduler.src.schemas.meeting import MeetingSchema
from meeting_scheduler.src.schemas.request import RequestSchema
from meeting_scheduler.src.schemas.timeslot import TimeslotSchema
from meeting_scheduler.src.schemas.user import UserSchema
from meeting_scheduler.src.utils import get_free_timeslots

db = app_factory.get_db()


class Smoke(Resource):
    def get(self):
        return {"status": "OK"}, 200


class UserApi(Resource):
    user_schema = UserSchema()
    user_db_service = CRUDService(User, db)

    def get(self, user_id: int = None):
        if user_id is None:
            users = self.user_db_service.get_all()
            return self.user_schema.dump(users, many=True), 200
        user = self.user_db_service.get(user_id)
        if not user:
            return "", 404
        return self.user_schema.dump(user), 200

    def post(self):
        user = self.user_schema.deserialize(request.json)
        if user:
            self.user_db_service.add(user)
            return self.user_schema.dump(user), 201
        return "", 400

    def put(self, user_id: int):
        user = self.user_db_service.get(user_id)
        if not user:
            return "", 404
        new_user = self.user_schema.deserialize(request.json)
        if new_user:
            update_json = {
                "username": new_user.username,
                "email": new_user.email,
                "password": new_user.password
            }
            self.user_db_service.update(user, update_json)
            return self.user_schema.dump(user), 200
        return "", 400

    def delete(self, user_id: int):
        user = self.user_db_service.get(user_id)
        if user:
            self.user_db_service.delete(user)
            return "", 204
        return "", 404


class MeetingApi(Resource):
    meeting_schema = MeetingSchema()
    request_schema = RequestSchema()
    meeting_db_service = CRUDService(Meeting, db)

    def get(self, meeting_id: int = None):
        if meeting_id is None:
            if request.args:
                req = self.request_schema.get_request(request.args)
                if req:
                    meetings = get_user_meetings(req)
                    return self.meeting_schema.dump(meetings, many=True), 200
            meetings = self.meeting_db_service.get_all()
            return self.meeting_schema.dump(meetings, many=True), 200
        meeting = self.meeting_db_service.get(meeting_id)
        if not meeting:
            return "", 404
        return self.meeting_schema.dump(meeting), 200

    def post(self):
        meeting = self.meeting_schema.deserialize(request.json)
        if meeting and dont_have_meeting_overlap(meeting) and \
                are_participants_have_timeslot(meeting):
            self.meeting_db_service.add(meeting)
            return self.meeting_schema.dump(meeting), 201
        return "", 400

    def put(self, meeting_id: int):
        meeting = self.meeting_db_service.get(meeting_id)
        if not meeting:
            return "", 404
        new_meeting = self.meeting_schema.deserialize(request.json)
        if new_meeting and dont_have_meeting_overlap(new_meeting, meeting) and \
                are_participants_have_timeslot(new_meeting):
            update_json = {
                "host_id": new_meeting.host.id,
                "participants": new_meeting.participants,
                "meeting_start_time": new_meeting.meeting_start_time,
                "meeting_end_time": new_meeting.meeting_end_time,
                "title": new_meeting.title,
                "details": new_meeting.details,
                "link": new_meeting.link,
                "comment": new_meeting.comment
            }
            self.meeting_db_service.update(meeting, update_json)
            return self.meeting_schema.dump(meeting), 200
        return "", 400

    def delete(self, meeting_id: int):
        meeting = self.meeting_db_service.get(meeting_id)
        if meeting:
            self.meeting_db_service.delete(meeting)
            return "", 204
        return "", 404


class TimeslotApi(Resource):
    timeslot_schema = TimeslotSchema()
    request_schema = RequestSchema()
    timeslot_db_service = CRUDService(Timeslot, db)

    def get(self, timeslot_id: int = None):
        if timeslot_id is None:
            if request.args:
                req = self.request_schema.get_request(request.args)
                if req:
                    return get_free_timeslots(req), 200
            timeslots = self.timeslot_db_service.get_all()
            return self.timeslot_schema.dump(timeslots, many=True), 200
        timeslot = self.timeslot_db_service.get(timeslot_id)
        if not timeslot:
            return "", 404
        return self.timeslot_schema.dump(timeslot), 200

    def post(self):
        timeslot = self.timeslot_schema.deserialize(request.json)
        if timeslot and dont_have_timeslot_overlap(timeslot):
            self.timeslot_db_service.add(timeslot)
            return self.timeslot_schema.dump(timeslot), 201
        return "", 400

    def put(self, timeslot_id: int):
        timeslot = self.timeslot_db_service.get(timeslot_id)
        if not timeslot:
            return "", 404
        new_timeslot = self.timeslot_schema.deserialize(request.json)
        if new_timeslot and dont_have_timeslot_overlap(new_timeslot, timeslot):
            update_json = {
                "start_time": new_timeslot.start_time,
                "end_time": new_timeslot.end_time,
                "user": new_timeslot.user.id
            }
            self.timeslot_db_service.update(timeslot, update_json)
            return self.timeslot_schema.dump(timeslot), 200
        return "", 400

    def delete(self, timeslot_id: int):
        timeslot = self.timeslot_db_service.get(timeslot_id)
        if timeslot:
            self.timeslot_db_service.delete(timeslot)
            return "", 204
        return "", 404
