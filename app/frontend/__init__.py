# -*- coding: utf-8 -*-
from flask import (Blueprint, render_template, request,
    current_app, send_from_directory, redirect)

frontend = Blueprint('frontend', __name__, template_folder="templates")

from .views import *


