import datetime
from flask import session
from flask_restful import Resource
from flask_login import login_required
from flask_jwt_extended import current_user, jwt_required

from app.extensions import db
from app.models import *
from app.api.shemes import *
from app.utils import *


class ServerTimeResource(Resource):
    def get(self):
        current_time = datetime.now()
        return current_time.strftime("%m.%d.%Y, %H:%M:%S")


class TerminalResource(Resource):
    @login_required
    def get(self):
        resp = dict()
        if find_key_dict("device", session):
            query = db.session.query(Device).filter(Device.id == session["device"]).first()
            if not query:
                resp["error"] = "device not found"
                return
            device_schema = DeviceSchema()
            service_schema = ServiceSchema(many=True)
            resp["organization"] = query.location_device.location_company.name
            resp["location"] = query.location_device.name
            resp["device"] = device_schema.dump(query)
            resp["services"] = service_schema.dump(query.location_device.services)
        return resp




