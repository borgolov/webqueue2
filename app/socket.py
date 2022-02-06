from flask import current_app, request, copy_current_request_context, session
from flask_login import current_user
from flask_socketio import emit, join_room, leave_room, close_room, rooms, disconnect, Namespace
from app import socket_io
from app.models import *
from .queue import *
from .utils import *


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
                qu = self.find_queue(worker.location_operator.id)
                if qu is not None:
                    if qu.join_in_place(worker, request.sid):
                        resp["room_id"] = worker.location_operator.name
                        resp["user"] = current_user.username
                        join_room(resp["room_id"], request.sid)
                        emit('settings', resp)
                    else:
                        self.on_disconnect()
        else:
            if find_key_dict("device", session):
                dev = db.session.query(Device).filter_by(id=session["device"]).first()
                if dev:
                    if self.find_queue(dev.location_device.id):
                        resp["room_id"] = dev.location_device.name
                        resp["device"] = dev.name
                        join_room(resp["room_id"], request.sid)
                        emit('settings', resp)

    def on_disconnect(self):
        if current_user.is_authenticated:
            worker = db.session.query(Operator).filter(Operator.user_operator == current_user).first()
            if worker:
                for place in self.queues:
                    if place.id == worker.location_operator.id:
                        place.leave_from_place(worker)
        disconnect(sid=request.sid, namespace=self)

    def on_my_event(self, data):
        emit('for_testing', data)

    def on_room_message(self, data):
        emit('for_testing', data, room=data['room'], broadcast=True)

    def on_take_ticket(self, data):
        """событие регистрации талона"""
        resp = {"room_id": "guest"}
        que = self.find_queue_on_user()
        if que:
            service = db.session.query(Service).filter(Service.id == data["service_id"]).first()
            if service:
                que.reg_ticket(service)
                resp["room_id"] = data["room"]
                resp["service"] = dict()
                resp["service"]["id"] = service.id
                resp["service"]["name"] = service.name
                emit('for_testing', resp, room=data['room'])
            else:
                resp["room_id"] = data["room"]
                resp["error"] = "services not found"
                emit('for_testing', resp, room=data['room'])

    def on_call_client(self, data):
        """событие вызова талона"""
        resp = {"room_id": data['room']}
        que = self.find_queue_on_user()
        if que:
            ticket = que.get_fifo_ticket(0)
            if ticket:
                worker = db.session.query(Operator).filter(Operator.user_operator == current_user).first()
                ticket.set_operator(worker.id)
                service = db.session.query(Service).filter(Service.id == ticket.service).first()
                resp["ticket"] = dict()
                resp["ticket"]["id"] = str(ticket.id)
                resp["ticket"]["time"] = str(ticket.create_time)
                resp["ticket"]["num"] = ticket.prefix + str(ticket.num)
                resp["ticket"]["service"] = dict()
                resp["ticket"]["service"]["id"] = service.id
                resp["ticket"]["service"]["name"] = service.name
                emit('for_testing', resp, room=data['room'])
                return
        resp["error"] = "ticket not found"
        emit('for_testing', resp, room=data['room'])

    def on_delay_client(self, data):
        pass

    def on_discard_client(self, data):
        pass

    def on_get_state_queue(self, data):
        """полу4ить статус очереди"""
        resp = {"room_id": data['room']}
        que = self.find_queue_on_user()
        if que:
            resp['tickets_in_queue'] = que.get_count_tickets(0)
            resp['tickets_treatment'] = que.get_count_tickets(1)
            resp['tickets_delayed'] = que.get_count_tickets(2)
            resp['tickets_discarded'] = que.get_count_tickets(3)
            emit('for_testing', resp)
            return
        resp['error'] = 'queue not found'
        emit('for_testing', resp)

    def on_get_ticket(self, data):
        pass

    def find_queue(self, id):
        """Поиск нужной очереди"""
        for place in self.queues:
            if place.id == id:
                return place
        return None

    def find_queue_on_user(self):
        """Поиск нужной очереди по воркеру"""
        if current_user.is_authenticated:
            worker = db.session.query(Operator).filter(Operator.user_operator == current_user).first()
            if worker:
                return self.find_queue(worker.location_operator.id)
