from flask import current_app, request, copy_current_request_context
from flask_socketio import emit, join_room, leave_room, \
    close_room, rooms, disconnect
from app import socket_io

namespace = '/queue'


@socket_io.on('connect', namespace=namespace)
def connect():
    current_app.logger.info('connect client: ' + str(request.remote_addr))
    current_app.logger.info('client sid: ' + request.sid)
    emit('api_response', {'data': request.sid})


@socket_io.on('join', namespace=namespace)
def join(message):
    print(message['room'])
    join_room(message['room'])
    emit('api_response', {'data': rooms()})


@socket_io.on('disconnect_request', namespace=namespace)
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()

    emit('api_response',
         {'data': 'Disconnected!'},
         callback=can_disconnect)

    print('Disconnect Client sid: ', request.sid)


@socket_io.on('disconnect', namespace=namespace)
def disconnect():
    print('Client disconnected', request.sid)


@socket_io.on('event_message', namespace=namespace)
def test_message(message):
    print(message['data'])
    emit('api_response', {'data': message['data']})


@socket_io.on('broadcast_message', namespace=namespace)
def broadcast_message(message):
    emit('api_response', {'data': message['data']}, broadcast=True)


@socket_io.on('send_room_message', namespace=namespace)
def send_room_message(message):
    emit('api_response', {'data': message['data']}, room=message['room'])
