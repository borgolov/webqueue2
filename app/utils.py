from datetime import datetime
from flask import redirect
from flask_login import login_user
from .models import *


def get_current_time():
    """get system time"""
    return datetime.utcnow()


def find_key_dict(key, coll: dict):
    """find key in dict"""
    if key in coll.keys():
        return True
    return False


def auth(login: str, password: str):
    """authorizate"""
    user = db.session.query(User).filter_by(username=login).first()
    if user and user.check_password(password):
        login_user(user, False)