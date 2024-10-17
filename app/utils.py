import time
import datetime
from flask import redirect, session, request
from flask_login import login_user, current_user
from flask_socketio import emit, join_room
from .models import *
from .queue import *
from .extensions import queues


def get_current_time():
    """get system time"""
    return datetime.utcnow()


def find_key_dict(key, coll: dict):
    """find key in dict"""
    if key in coll.keys():
        return True
    return False


def authorizade(login: str, password: str):
    """authorizate"""
    user = db.session.query(User).filter_by(username=login).first()
    if user and user.check_password(password):
        login_user(user, False)


def find_queue(id: int, queues: list):
    """Поиск нужной очереди"""
    for que in queues:
        if que.id == id:
            return que


def find_queue_on_user(queues: list):
    """Поиск нужной очереди по воркеру"""
    if current_user.is_authenticated:
        worker = db.session.query(Operator).filter(Operator.user_operator == current_user).first()
        if worker:
            return find_queue(worker.location_operator.id, queues), worker


def find_queue_on_location(queues: list):
    """Поиск нужной очереди по локации"""
    if find_key_dict("location", session):
        location = db.session.query(Location).filter_by(id=session["location"]).first()
        if location:
            return find_queue(location.id, queues), location


def make_resp_on_queue(queue: Queue):
    """ответ о состоянии очереди"""
    resp = dict()
    resp["room_id"] = queue.name
    resp['tickets_in_queue'] = queue.get_count_tickets(0)
    resp['tickets_treatment'] = queue.get_count_tickets(1)
    resp['tickets_delayed'] = queue.get_count_tickets(2)
    resp['services'] = []
    for service in db.session.query(Location).filter_by(id=queue.id).first().services:
        resp['services'].append({'service': {'id': service.id, 'name': service.name, 'count': queue.get_count_tickets_on_service(service.id, 0),
                                             'count_delay': queue.get_count_tickets_on_service(service.id, 2)}})
    resp['treatment'] = []
    for ticket in queue.get_treatment_ticket():
        treat = dict()
        treat["operator"] = dict()
        treat["operator"]["id"] = ticket.operator_id
        treat["operator"]["name"] = db.session.query(Operator).filter_by(id=ticket.operator_id).first().name
        treat.update(make_resp_on_ticket(ticket))
        resp['treatment'].append(treat)
    return resp


def make_resp_on_ticket(ticket: Ticket):
    """ответ тикета"""
    resp = dict()
    resp["ticket"] = dict()
    resp["ticket"]["id"] = str(ticket.id)
    resp["ticket"]["time"] = str(ticket.create_time)
    resp["ticket"]["num"] = str(ticket.num)
    resp["ticket"]["prefix"] = ticket.prefix
    resp["ticket"]["service"] = dict()
    resp["ticket"]["service"]["id"] = ticket.service
    resp["ticket"]["service"]["name"] = ticket.service_name
    return resp


def socket_interaction(queues: list):
    """поиск объектов для взаимодействия с очередью"""
    result = dict()
    if current_user.is_authenticated:
        if current_user.has_role('superuser'):
            result["queue"], result["location"] = find_queue_on_location(queues)
            result["room"] = str(result["location"].id)
        elif current_user.has_role('operator'):
            result["queue"], result["operator"] = find_queue_on_user(queues)
            result["location"] = result["operator"].location_operator
            result["room"] = str(result["location"].id)
    return result


def socket_connect(queues: list):
    """подключение к системе клиентов"""
    resp = {"room_id": "guest"}
    interactions = socket_interaction(queues)
    if interactions['queue']:
        if find_key_dict('location', interactions):
            join_room(interactions["room"], request.sid)
            resp["room_id"] = str(interactions['room'])
            emit('settings', resp)
            emit('state', make_resp_on_queue(interactions['queue']), room=str(interactions['room']))
        elif find_key_dict('operator', interactions):
            join_room(str(interactions['room']), request.sid)
            resp["room_id"] = interactions['operator'].location_operator.id
            resp["user"] = current_user.username
            emit('settings', resp)


def take_ticket(queues: list, data: dict):
    """заказ талона"""
    resp = {"room_id": data["room"]}
    interactions = socket_interaction(queues)
    service = db.session.query(Service).filter(Service.id == data["service_id"]).first()
    if interactions['queue'] and service:
        if find_key_dict('location', interactions):
            print(data["priority"])
            ticket = interactions['queue'].reg_ticket(service, data["priority"] if data["priority"] else 0)
            resp.update(make_resp_on_ticket(ticket))
            emit('last_ticket', resp)
            emit('state', make_resp_on_queue(interactions['queue']), room=interactions['room'], broadcast=True)
            emit('for_testing', resp)
            emit('for_testing', make_resp_on_queue(interactions['queue']), room=interactions['room'], broadcast=True)
            emit('newticket', resp, room=interactions['room'], broadcast=True)
            return
    resp["room_id"] = data["room"]
    resp["error"] = "services not found"
    emit('last_ticket', resp)
    emit('for_testing', resp)


def get_ids_services_on_operator(operator: Operator):
    """формирование сристка id услуг по оператору"""
    service_pool = []
    for service in operator.services:
        service_pool.append(service.id)
    return service_pool


def call_client(queues: list, data: dict, state: int):
    """вызвать первого из очереди"""
    resp = {"room_id": data["room"]}
    interactions = socket_interaction(queues)
    if interactions['queue'] and interactions['operator']:
        service_pool = get_ids_services_on_operator(interactions['operator'])
        resp['operator'] = {
            'id': interactions['operator'].id,
            'name':  interactions['operator'].name,
            'duber': interactions['operator'].duber
        }
        if not interactions['queue'].is_free_worker(interactions['operator'].id):
            resp["error"] = "worker not free"
            treatment = interactions['queue'].get_ticket_on_worker(interactions['operator'].id, 1)
            resp.update(make_resp_on_ticket(treatment))
            emit('call_client', resp, room=interactions['room'], broadcast=True)
            emit('for_testing', resp, room=request.sid)
            return
        else:
            ticket = interactions['queue'].get_fifo_ticket_priority(state, service_pool)
            if ticket:
                interactions['queue'].take_service(ticket.id)
                ticket.set_operator(interactions['operator'].id)
                resp.update(make_resp_on_ticket(ticket))
                emit('for_testing', make_resp_on_queue(interactions['queue']), room=interactions['room'], broadcast=True)
                emit('for_testing', resp, room=request.sid)

                emit('for_operator', resp, room=request.sid)
                emit('last_ticket', resp)
                emit('state', make_resp_on_queue(interactions['queue']), room=interactions['room'], broadcast=True)
                emit('call_client', resp, room=data['room'], broadcast=True)
                emit('ticket', resp, room=request.sid)
                return
            resp["error"] = "ticket not found"
            emit('for_testing', resp, room=request.sid)


def delay_client(queues: list, data: dict):
    """отложить клиента"""
    resp = {"room_id": data["room"]}
    interactions = socket_interaction(queues)
    if interactions['queue'] and interactions['operator']:
        ticket = interactions['queue'].get_ticket_on_worker(interactions['operator'].id, 1)
        ticket.set_operator()
        ticket.status = 2
        resp["status"] = "delayed!!!"
        resp.update(make_resp_on_ticket(ticket))
        emit('for_testing', make_resp_on_queue(interactions['queue']), room=data["room"], broadcast=True)
        emit('for_testing', resp, room=request.sid)
        emit('state', make_resp_on_queue(interactions['queue']), room=data['room'], broadcast=True)
        emit('ticket', room=request.sid)


def confirm_client(queues: list, data: dict):
    """завершить с клиентом прием"""
    resp = {"room_id": data["room"]}
    interactions = socket_interaction(queues)
    if interactions['queue'] and interactions['operator']:
        ticket = interactions['queue'].success_ticket(interactions['operator'].id)
        if ticket:
            resp["status"] = "successed!!!"
            resp.update(make_resp_on_ticket(ticket))
            emit('for_testing', make_resp_on_queue(interactions['queue']), room=data['room'], broadcast=True)
            emit('for_testing', resp, room=request.sid)
            emit('state', make_resp_on_queue(interactions['queue']), room=interactions['room'], broadcast=True)
            emit('ticket', room=request.sid)
            return
        resp["error"] = "empty"
        emit('for_testing', resp, room=request.sid)


def get_state_queue(queues: list, data: dict):
    """получить состояние очереди"""
    resp = {"room_id": data["room"]}
    interactions = socket_interaction(queues)
    if interactions['queue']:
        emit('state', resp.update(make_resp_on_queue(interactions['queue'])), room=request.sid)
        emit('for_testing', resp, room=request.sid)


def change_service_client(queues: list, data: dict):
    """сменить услугу клиенту"""
    resp = {"room_id": data["room"]}
    interactions = socket_interaction(queues)
    service = db.session.query(Service).filter(Service.id == data["service_id"]).first()
    if interactions['queue'] and interactions['operator'] and service:
        ticket = interactions['queue'].get_ticket_on_worker(interactions['operator'].id, 1)
        ticket.set_service(service)
        ticket.set_operator()
        ticket.status = 0
        resp["status"] = "redirected!!!"
        resp.update(make_resp_on_ticket(ticket))
        emit('state', make_resp_on_queue(interactions['queue']), room=interactions['room'], broadcast=True)
        emit('ticket', room=request.sid)
        emit('for_testing', make_resp_on_queue(interactions['queue']), room=interactions['room'], broadcast=True)
        emit('for_testing', resp, room=request.sid)


def get_ticket(queues: list):
    """получить текущий тиекет"""
    interactions = socket_interaction(queues)
    resp = {"room_id": interactions["room"]}
    if interactions['queue'] and interactions['operator']:
        if not interactions['queue'].is_free_worker(interactions['operator'].id):
            ticket = interactions['queue'].get_ticket_on_worker(interactions['operator'].id, 1)
            if ticket:
                resp.update(make_resp_on_ticket(ticket))
                emit('ticket', resp, room=request.sid)
                emit('for_testing', resp, room=request.sid)
    emit('ticket', room=request.sid)
    emit('for_testing', resp, room=request.sid)


def clear_queue_on_time():
    """очистить очереди по времени"""
    while True:
        now = datetime.now()
        today = now.replace(hour=22, minute=00, second=0, microsecond=0)
        if now > today:
            for queue in queues:
                queue.reset_queue()
        else:
            pass
        time.sleep(60)