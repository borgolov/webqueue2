import datetime
from .models import *


class Ticket:
    def __init__(self):
        self.num = 0
        self.prefix = ''
        self.create_time = datetime.datetime.now()
        self.operator_id = None

    def set_operator(self, id=None):
        self.operator_id = id


class Queue:
    def __init__(self, location: Location):
        self.id = location.id
        self.name = location.name
        self.tickets = []
        self.delayed_tickets = []
        self.tickets_discard = []
        self.sockets = []

    def join_in_place(self, worker_id, sid):
        sockets = next((d for d in self.sockets if worker_id in d), None)
        if sockets:
            return False
        else:
            self.sockets.append({worker_id: sid})
            return True

    def leave_from_place(self, sid):
        for d in self.sockets:
            for key, value in d.items():
                if value == sid:
                    self.sockets.remove(d)