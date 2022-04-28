from flask import render_template, request
from flask_login import login_required, logout_user
from app.models import *

from app.extensions import login_manager, my_sessions
from app.auth import auth
from app.utils import *


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/auth')


@auth.route('/auth', methods=['POST', 'GET'])
def login():
    """пользователь ранее был авторизован"""
    if current_user.is_authenticated:
        return redirect("/")
    if request.method == 'POST' and 'signin' in request.form:
        username = str(request.form['InputUserName'])
        password = str(request.form['InputPassword'])
        authorizade(username, password)
        return redirect("/")
    return render_template('login_form.html')


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).filter_by(id=user_id).first()


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop("location")
    return redirect('/auth')