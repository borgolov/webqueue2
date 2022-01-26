import datetime
from flask import request, jsonify, json, make_response
from flask_restful import Resource
from flask_jwt_extended import current_user, jwt_required

from app.extensions import db
from app.models import *


class ServerTimeResource(Resource):
    def get(self):
        current_time = datetime.now()
        return current_time.strftime("%m.%d.%Y, %H:%M:%S")


