import datetime, uuid
from .models import *


class Ticket:
    def __init__(self, service: Service, num):
        self.id = uuid.uuid4()
        self.num = num
        self.prefix = service.prefix
        self.create_time = datetime.now()
        self.service = service.id
        self.service_name = service.name
        self.operator_id = None
        self.status = 0 # 0 - in queue, 1 - taken_operator, 2 - delayed, 3 - discard

    def set_operator(self, id=None):
        self.operator_id = id

    def set_service(self, service: Service):
        self.service = service.id
        self.service_name = service.name


class Queue:
    def __init__(self, location: Location):
        self.id = location.id
        self.name = location.name
        self.tickets = []
        self.sockets = [] # connected operators

    def join_in_place(self, operator: Operator, sid):
        pass

    def leave_from_place(self, operator: Operator):
        pass

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

    def get_ticket_on_worker(self, worker_id, status):
        for ticket in self.tickets:
            if ticket.operator_id == worker_id and ticket.status == status:
                return ticket

    def reg_ticket(self, service: Service):
        ticket = Ticket(service, self.get_count_tickets(0) + 1)
        self.tickets.append(ticket)
        return ticket

    def success_ticket(self, worker_id):
        ticket = self.get_ticket_on_worker(worker_id, 1)
        if ticket:
            self.tickets.remove(ticket)
            return ticket

    def delay_ticket(self, uid):
        self.get_ticket(uid).status = 2

    def discard_ticket(self, uid):
        self.get_ticket(uid).status = 3

    def take_service(self, uid):
        ticket = self.get_ticket(uid)
        if ticket:
            ticket.status = 1
            return ticket

    def get_fifo_ticket(self, status, service_pool: list):
        for ticket in self.tickets:
            if ticket.status == status:
                if set([ticket.service]).issubset({service for service in service_pool}):
                    return ticket

    def is_free_worker(self, worker_id):
        if self.get_ticket_on_worker(worker_id, 1) is not None:
            return False
        return True

    def del_ticket(self, uid):
        ticket = self.get_ticket(uid)
        self.tickets.remove(ticket)

    def reset_queue(self):
        self.tickets = []
        self.sockets = []

    def get_treatment_ticket(self):
        array = list()
        for ticket in self.tickets:
            if ticket.status == 1:
                array.append(ticket)
        return array
