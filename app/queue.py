import datetime, uuid
from .models import *


class Worker:
    def __init__(self, operator: Operator, sid):
        self.id = operator.id
        self.name = operator.name
        self.sid = sid


class Ticket:
    def __init__(self, service: Service):
        self.id = uuid.uuid4()
        self.num = 0
        self.prefix = ''
        self.create_time = datetime.datetime.now()
        self.service = service.id
        self.service_name = service.name
        self.operator_id = None
        self.status = 0 # 0 - in queue, 1 - taken_operator, 2 - delayed, 3 - discard

    def set_operator(self, id=None):
        self.operator_id = id


class Queue:
    def __init__(self, location: Location):
        self.id = location.id
        self.name = location.name
        self.tickets = []
        self.sockets = [] # connected operators

    def join_in_place(self, operator: Operator, sid):
        for worker in self.sockets:
            if worker.sid == sid:
                return False
        self.sockets.append(Worker(operator, sid))
        return True

    def leave_from_place(self, operator: Operator):
        for d in self.sockets:
            if d == operator:
                self.sockets.remove(d)

    def get_count_tickets(self, status: int):
        count = 0
        for ticket in self.tickets:
            if ticket.status == status:
                count += 1
        return count

    def get_ticket(self, uid):
        for ticket in self.tickets:
            if ticket.id == uid:
                return ticket

    def reg_ticket(self, service: Service):
        self.tickets.append(Ticket(service))

    def delay_ticket(self, uid):
        self.get_ticket(uid).status = 2

    def discard_ticket(self, uid):
        self.get_ticket(uid).status = 3

    def take_service(self, uid):
        self.get_ticket(uid).status = 1

    def get_fifo_ticket(self, status):
        for ticket in self.tickets:
            if ticket.status == status:
                return ticket
