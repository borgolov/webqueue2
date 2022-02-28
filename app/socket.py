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
        socket_connect(self.queues)

    def on_disconnect(self):
        disconnect(sid=request.sid, namespace=self)

    def on_take_ticket(self, data):
        """событие регистрации талона"""
        take_ticket(self.queues, data)

    def on_call_client(self, data):
        """событие вызова талона"""
        call_client(self.queues, data)

    def on_call_delay_client(self, data):
        """событие вызова талона"""
        call_delay_client(self.queues, data)

    def on_delay_client(self, data):
        """отложить тикет"""
        delay_client(self.queues, data)

    def on_confirm_client(self, data):
        """завершить работу с клиентом"""
        confirm_client(self.queues, data)

    def on_get_state_queue(self, data):
        """полу4ить статус очереди"""
        get_state_queue(self.queues, data)

    def on_get_ticket(self, data):
        pass

    def on_change_service_client(self, data):
        """сменить услугу у тикета"""
        change_service_client(self.queues, data)

