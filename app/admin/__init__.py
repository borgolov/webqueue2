from app import adm, db
from flask import (Blueprint, render_template, request,
    current_app, send_from_directory, redirect, url_for)
from flask_admin import expose
from flask_admin.contrib.sqlamodel import ModelView
from flask_admin import AdminIndexView
from flask_login import current_user
from app.models import *

admin_bp = Blueprint('admin_bp', __name__, template_folder="templates")
adm.name = 'Web QUEUE'
adm.template_mode = 'bootstrap4'


class MicroBlogModelView(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.has_role("superuser")
        return False

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect('/auth')


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.has_role("superuser")
        return False

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect('/auth')


adm.add_view(MicroBlogModelView(User, db.session))
adm.add_view(MicroBlogModelView(Company, db.session))
adm.add_view(MicroBlogModelView(Role, db.session))
adm.add_view(MicroBlogModelView(Location, db.session))
adm.add_view(MicroBlogModelView(Service, db.session))
adm.add_view(MicroBlogModelView(DeviceType, db.session))
adm.add_view(MicroBlogModelView(Device, db.session))
adm.add_view(MicroBlogModelView(Operator, db.session))