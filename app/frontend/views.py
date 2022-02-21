import os
from flask import render_template, request, current_app, send_from_directory, redirect, jsonify, url_for, session
from flask_login import current_user, login_user, login_required, logout_user
from app.models import *

from app.extensions import login_manager, my_sessions
from app.frontend import frontend
from app.utils import *


@frontend.route('/')
@login_required
def main():
    print(session)
    return render_template('home.html', user=current_user.username)


@frontend.route('/simple_chat')
def simple_chat():
    return render_template('simple_chat.html')


@frontend.route('/api_tester')
def api_tester():
    return render_template('api_tester.html')


@frontend.route('/device', methods=['POST', 'GET'])
@login_required
def device():
    if current_user.has_role('device'):
        if request.method == 'POST' and 'inputSelect' in request.form:
            dev = db.session.query(Device).filter_by(id=request.form['inputDevice']).first()
            if dev:
                session["device"] = dev.id
        if find_key_dict("device", session):
            dev = db.session.query(Device).filter_by(id=session["device"]).first()
            if dev and dev.has_type('Терминал'):
                return render_template('terminal.html')
        else:
            devices = db.session.query(Device).all()
            return render_template('device_reg_form.html', list=devices)
    return redirect('/auth')


@frontend.route('/exitdevice', methods=['POST', 'GET'])
def exit_device():
    session.pop("device")
    return redirect('/device')


@frontend.route('/ticket', methods=['GET'])
def ticket_template():
    if request.args.get('template'):
        template = request.args.get('template')
        if os.path.isfile(f'{current_app.root_path}/templates/ticket_template/{template}.html'):
            return render_template(f'ticket_template/{template}.html', data=request.args.to_dict())
    return render_template(f'ticket_template/default.html', data=request.args.to_dict())