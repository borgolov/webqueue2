from app.api import api
from app.api.resources import *

api.add_resource(ServerTimeResource, '/server_time')
api.add_resource(TerminalResource, '/device_settings')
api.add_resource(OperatorResource, '/operator_settings')