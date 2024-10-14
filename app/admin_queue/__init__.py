from sqlalchemy import inspect
from app import adm, db
from flask import (Blueprint, render_template, request,
    current_app, send_from_directory, redirect, url_for)
from flask_admin import expose
from flask_admin.model.form import InlineFormAdmin
from flask_admin.form import SecureForm
from wtforms import PasswordField, Form, SelectField, IntegerField, FieldList, FormField
from wtforms.validators import DataRequired
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView
from flask_login import current_user
from app.models import *

admin_bp = Blueprint('admin_bp', __name__, template_folder="templates")
adm.name = 'Web QUEUE'
adm.template_mode = 'bootstrap4'


class MicroBlogModelView(ModelView):
    column_diplay_pk = True
    column_hide_backrefs = False
    
    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.has_role("superuser")
        return False

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect('/auth')
    

class OperatorView(MicroBlogModelView):
    column_list = [c_attr.key for c_attr in inspect(Operator).mapper.column_attrs]
    


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.has_role("superuser")
        return False

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect('/auth')


class UserView(ModelView):
    
    form_base_class = SecureForm
    column_list = ['name', 'active', 'username']
    column_editable_list = ['name', 'active', 'username']
    form_columns = ['name', 'active', 'username', 'password']
    form_extra_fields = {
        'password': PasswordField('Password')
    }

    def on_model_change(self, form, model, is_created):
        # Если поле пароля было заполнено в форме, обновляем хэш пароля
        if form.password.data:
            model.set_password(form.password.data)


adm.add_view(UserView(User, db.session))
adm.add_view(MicroBlogModelView(Company, db.session))
adm.add_view(MicroBlogModelView(Role, db.session))
adm.add_view(MicroBlogModelView(Location, db.session))
adm.add_view(MicroBlogModelView(Service, db.session))
adm.add_view(OperatorView(Operator, db.session))
adm.add_view(MicroBlogModelView(ServiceLocationOffset, db.session))