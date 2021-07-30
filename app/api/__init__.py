# -*- coding: utf-8 -*-
from flask import Blueprint, current_app, jsonify
from marshmallow import ValidationError
from flask_restful import Api

restful_api = Blueprint("api", __name__, url_prefix="/api/v1")
api = Api(restful_api)

from .views import *


@restful_api.errorhandler(ValidationError)
def handle_marshmallow_error(e):
    """Return json error for marshmallow validation errors.
    This will avoid having to try/catch ValidationErrors in all endpoints, returning
    correct JSON response with associated HTTP 400 Status (https://tools.ietf.org/html/rfc7231#section-6.5.1)
    """
    return jsonify(e.messages), 400
