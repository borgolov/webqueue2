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
    return render_template('home.html', current_user=current_user)


@frontend.route('/simple_chat')
def simple_chat():
    return render_template('simple_chat.html')


@frontend.route('/api_tester')
def api_tester():
    return render_template('api_tester.html')


@frontend.route('/terminal', methods=['POST', 'GET'])
@login_required
def terminal():
    if not current_user.has_role('superuser'):
        return "permition denied"
    if request.method == 'POST' and 'inputSelect' in request.form:
        location = db.session.query(Location).filter_by(id=request.form['inputDevice']).first()
        if location:
            session["location"] = location.id
    if find_key_dict("location", session):
        location = db.session.query(Location).filter(Location.id == session['location']).first()
        if location:
            return render_template('terminal.html')
    locations = db.session.query(Location).all()
    return render_template('device_reg_form.html', list=locations)


@frontend.route('/screen', methods=['POST', 'GET'])
@login_required
def screen():
    if not current_user.has_role('superuser'):
        return "permition denied"
    if request.method == 'POST' and 'inputSelect' in request.form:
        location = db.session.query(Location).filter_by(id=request.form['inputDevice']).first()
        if location:
            session["location"] = location.id
    if find_key_dict("location", session):
        location = db.session.query(Location).filter(Location.id == session['location']).first()
        if location:
            return render_template('screen.html')
    locations = db.session.query(Location).all()
    return render_template('device_reg_form.html', list=locations)


@frontend.route('/exitdevice', methods=['POST', 'GET'])
def exit_device():
    session.pop("location")
    return redirect('/')


@frontend.route('/worker', methods=['POST', 'GET'])
def worker():
    return render_template('worker.html')


@frontend.route('/ticket', methods=['GET'])
def ticket_template():
    if request.args.get('template'):
        template = request.args.get('template')
        if os.path.isfile(f'{current_app.root_path}/templates/ticket_template/{template}.html'):
            return render_template(f'ticket_template/{template}.html', data=request.args.to_dict())
    return render_template(f'ticket_template/default.html', data=request.args.to_dict())