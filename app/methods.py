from flask import current_app, request, copy_current_request_context
from flask_login import current_user
from flask_socketio import emit, join_room, leave_room, close_room, rooms, disconnect, Namespace
from app import socket_io
from app.models import *
from .queue import *


class MyCustomNamespace(Namespace):
    def __init__(self, namespace=None):
        super(MyCustomNamespace, self).__init__(namespace)
        self.queues = list()
        locations = db.session.query(Location).all()
        for locate in locations:
            queue = Queue(locate)
            self.queues.append(queue)

    def on_connect(self):
        current_app.logger.info(f'connect client: {request.sid} , {str(request.remote_addr)}.')
        resp = {"room_id": "guest"}
        if current_user.is_authenticated:
            if current_user.has_role('superuser'):
                resp["room_id"] = 'superuser'
                resp["user"] = current_user.username
                join_room(resp["room_id"], request.sid)
                emit('settings', resp)
                return
            worker = db.session.query(Operator).filter(Operator.user_operator == current_user).first()
            if worker:
                for place in self.queues:
                    if place.id == worker.location_operator.id:
                        if place.join_in_place(worker.id, request.sid):
                            resp["room_id"] = place.name
                            resp["user"] = current_user.username
                            join_room(resp["room_id"], request.sid)
                            emit('settings', resp)
                        else:
                            self.on_disconnect()

    def on_disconnect(self):
        if current_user.is_authenticated:
            worker = db.session.query(Operator).filter(Operator.user_operator == current_user).first()
            if worker:
                for place in self.queues:
                    if place.id == worker.location_operator.id:
                        place.leave_from_place(request.sid)
        disconnect(sid=request.sid, namespace=self)

    def on_my_event(self, data):
        emit('for_testing', data)

    def on_room_message(self, data):
        emit('for_testing', data, room=data['room'], broadcast=True)
