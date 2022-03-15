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
        if find_key_dict("location", session):
            query = db.session.query(Location).filter(Location.id == session["location"]).first()
            if not query:
                resp["error"] = "location not found"
                return resp
            service_schema = ServiceSchema(many=True)
            resp["organization"] = query.location_company.name
            resp["location"] = query.name
            resp["services"] = service_schema.dump(query.services)
        return resp


class OperatorResource(Resource):
    @login_required
    def get(self):
        resp = dict()
        operator = db.session.query(Operator).filter(Operator.user_operator == current_user).first()
        if not operator:
            resp["error"] = "device not found"
            return resp
        schema = OperatorSchema()
        service_schema = ServiceSchema(many=True)
        resp["organization"] = operator.location_operator.location_company.name
        resp["location"] = operator.location_operator.name
        resp["operator"] = schema.dump(operator)
        resp["services"] = service_schema.dump(operator.location_operator.services)
        return resp

