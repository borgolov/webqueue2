from datetime import datetime
from flask import redirect, session
from flask_login import login_user, current_user
from .models import *
from .queue import *


def get_current_time():
    """get system time"""
    return datetime.utcnow()


def find_key_dict(key, coll: dict):
    """find key in dict"""
    if key in coll.keys():
        return True
    return False


def auth(login: str, password: str):
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
            return find_queue(worker.location_operator.id, queues)


def find_queue_on_device(queues: list):
    """Поиск нужной очереди по устройству"""
    if find_key_dict("device", session):
        dev = db.session.query(Device).filter_by(id=session["device"]).first()
        if dev:
            return find_queue(dev.location_device.id, queues)


def make_resp_on_queue(queue: Queue):
    """ответ о состоянии очереди"""
    resp = dict()
    resp["room_id"] = queue.name
    resp['tickets_in_queue'] = queue.get_count_tickets(0)
    resp['tickets_treatment'] = queue.get_count_tickets(1)
    resp['tickets_delayed'] = queue.get_count_tickets(2)
    resp['tickets_discarded'] = queue.get_count_tickets(3)
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