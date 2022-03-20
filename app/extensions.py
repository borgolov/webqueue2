# -*- coding: utf-8 -*-
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_login import LoginManager
from flask_admin import Admin
from flask_session import Session
from flask_marshmallow import Marshmallow


db = SQLAlchemy()
bcrypt = Bcrypt()
migrate = Migrate()
ma = Marshmallow()
socket_io = SocketIO()
login_manager = LoginManager()
adm = Admin()
my_sessions = Session()
ma = Marshmallow()
queues = []