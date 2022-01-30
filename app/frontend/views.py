from flask import render_template, request, current_app, send_from_directory, redirect, jsonify, url_for, session
from flask_login import current_user, login_user, login_required, logout_user
from app.models import *

from app.extensions import login_manager, my_sessions
from app.frontend import frontend
from app.utils import *


@frontend.route('/')
@login_required
def main():
    return render_template('home.html', user=current_user.username)


@frontend.route('/auth', methods=['POST', 'GET'])
def login():
    """пользователь ранее был авторизован"""
    if current_user.is_authenticated:
        return redirect("/")
    if request.method == 'POST' and 'signin' in request.form:
        username = str(request.form['InputUserName'])
        password = str(request.form['InputPassword'])
        auth(username, password)
    return render_template('login_form.html')


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).filter_by(id=user_id).first()


@frontend.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/auth')


@frontend.route('/simple_chat')
def simple_chat():
    return render_template('simple_chat.html')


@frontend.route('/api_tester')
def api_tester():
    return render_template('api_tester.html')


@frontend.route('/device', methods=['POST', 'GET'])
def device():
    if request.method == 'POST' and 'inputSelect' in request.form:
        dev = db.session.query(Device).filter_by(id=request.form['inputDevice']).first()
        if dev:
            session["device"] = dev.id
    if find_key_dict("device", session):
        return render_template('api_tester.html')
    else:
        devices = db.session.query(Device).all()
        return render_template('device_reg_form.html', list=devices)


@frontend.route('/exitdevice', methods=['POST', 'GET'])
def exit_device():
    session.pop("device")
    return redirect('/device')