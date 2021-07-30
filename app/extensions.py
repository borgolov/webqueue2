# -*- coding: utf-8 -*-
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_socketio import SocketIO


bcrypt = Bcrypt()
db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
socket_io = SocketIO()
