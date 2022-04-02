from flask import current_app, request, copy_current_request_context, session
from flask_login import current_user
from flask_socketio import emit, join_room, leave_room, close_room, rooms, disconnect, Namespace
from app import socket_io
from app.models import *
from .queue import *
from .utils import *
from app import queues


class MyCustomNamespace(Namespace):
    @staticmethod
    def on_connect():
        socket_connect(queues)

    def on_disconnect(self):
        disconnect(sid=request.sid, namespace=self)

    @staticmethod
    def on_take_ticket(data):
        """событие регистрации талона"""
        take_ticket(queues, data)

    @staticmethod
    def on_call_client(data):
        """событие вызова талона"""
        call_client(queues, data, 0)

    @staticmethod
    def on_call_delay_client(data):
        """событие вызова талона"""
        call_client(queues, data, 2)

    @staticmethod
    def on_delay_client(data):
        """отложить тикет"""
        delay_client(queues, data)

    @staticmethod
    def on_confirm_client(data):
        """завершить работу с клиентом"""
        confirm_client(queues, data)

    @staticmethod
    def on_get_state_queue(data):
        """полу4ить статус очереди"""
        get_state_queue(queues, data)

    @staticmethod
    def on_get_ticket(data):
        get_ticket(queues)

    @staticmethod
    def on_change_service_client(data):
        """сменить услугу у тикета"""
        change_service_client(queues, data)

