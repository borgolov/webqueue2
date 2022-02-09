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
        #current_app.logger.info(f'connect client: {request.sid} , {str(request.remote_addr)}.')
        resp = {"room_id": "guest"}
        if current_user.is_authenticated:
            if current_user.has_role('superuser'):
                resp["room_id"] = 'superuser'
                resp["user"] = current_user.username
                join_room(resp["room_id"], request.sid)
                emit('settings', resp)
                return
            elif current_user.has_role('device'):
                if find_queue_on_device(self.queues):
                    dev = db.session.query(Device).filter(Device.id == session["device"]).first()
                    resp["room_id"] = dev.location_device.name
                    resp["device"] = dev.name
                    join_room(resp["room_id"], request.sid)
                    emit('settings', resp)
                return
            elif current_user.has_role('operator'):
                worker = db.session.query(Operator).filter(Operator.user_operator == current_user).first()
                if worker:
                    qu = find_queue(worker.location_operator.id, self.queues)
                    if qu is not None:
                        resp["room_id"] = worker.location_operator.name
                        resp["user"] = current_user.username
                        join_room(resp["room_id"], request.sid)
                        emit('settings', resp)

    def on_disconnect(self):
        disconnect(sid=request.sid, namespace=self)

    def on_my_event(self, data):
        emit('for_testing', data)

    def on_room_message(self, data):
        emit('for_testing', data, room=data['room'], broadcast=True)

    def on_take_ticket(self, data):
        """событие регистрации талона"""
        resp = {"room_id": data["room"]}
        que = find_queue_on_device(self.queues)
        if que:
            service = db.session.query(Service).filter(Service.id == data["service_id"]).first()
            if service:
                ticket = que.reg_ticket(service)
                resp.update(make_resp_on_ticket(ticket))
                emit('for_testing', resp)
                emit('for_testing', make_resp_on_queue(que), room=data['room'], broadcast=True)
            else:
                resp["room_id"] = data["room"]
                resp["error"] = "services not found"
                emit('for_testing', resp)

    def on_call_client(self, data):
        """событие вызова талона"""
        resp = {"room_id": data['room']}
        que = find_queue_on_user(self.queues)
        worker = db.session.query(Operator).filter(Operator.user_operator == current_user).first()
        if que:
            service_pool = []
            for service in worker.services:
                service_pool.append(service.id)
            ticket = que.get_fifo_ticket(0, service_pool)
            if ticket:
                if not que.is_free_worker(worker.id):
                    resp["error"] = "worker not free"
                    resp.update(make_resp_on_ticket(que.get_ticket_on_worker(worker.id, 1)))
                    emit('for_testing', resp, room=request.sid)
                    return
                que.take_service(ticket.id)
                ticket.set_operator(worker.id)
                resp.update(make_resp_on_ticket(ticket))
                emit('for_testing', make_resp_on_queue(que), room=data['room'], broadcast=True)
                emit('for_testing', resp, room=request.sid)
                return
        resp["error"] = "ticket not found"
        emit('for_testing', resp, room=request.sid)

    def on_delay_client(self, data):
        pass

    def on_discard_client(self, data):
        pass

    def on_confirm_client(self, data):
        """завершить работу с клиентом"""
        resp = dict()
        que = find_queue_on_user()
        if que:
            worker = db.session.query(Operator).filter(Operator.user_operator == current_user).first()
            ticket = que.success_ticket(worker.id)
            if ticket:
                resp["room_id"] = data["room"]
                resp["status"] = "successed!!!"
                resp.update(make_resp_on_ticket(ticket))
                emit('for_testing', make_resp_on_queue(que), room=data['room'], broadcast=True)
                emit('for_testing', resp, room=request.sid)
                return
            resp["error"] = "empty"
            emit('for_testing', resp, room=request.sid)

    def on_get_state_queue(self, data):
        """полу4ить статус очереди"""
        resp = {"room_id": data['room']}
        que_on_user = find_queue_on_user(self.queues)
        que_on_device = find_queue_on_device(self.queues)
        if que_on_user:
            emit('for_testing', make_resp_on_queue(que_on_user), room=data['room'], broadcast=True)
            return
        if que_on_device:
            emit('for_testing', make_resp_on_queue(que_on_device), room=data['room'], broadcast=True)
            return
        resp['error'] = 'queue not found'
        emit('for_testing', resp, room=data['room'])

    def on_get_ticket(self, data):
        pass

    def on_change_service_ticket(self, data):
        """сменить услугу у тикета"""
        resp = {"room_id": data['room']}
        service = db.session.query(Service).filter(Service.id == data["service_id"]).first()
        que = find_queue_on_user(self.queues)
        worker = db.session.query(Operator).filter(Operator.user_operator == current_user).first()
        if que:
            ticket = que.get_ticket_on_worker(worker.id, 1)
            ticket.set_service(service)
            ticket.status = 0
            resp["status"] = "redirected!!!"
            resp.update(make_resp_on_ticket(ticket))
            emit('for_testing', make_resp_on_queue(que), room=data["room"], broadcast=True)
            emit('for_testing', resp, room=request.sid)
