from flask import render_template, request, current_app, send_from_directory, redirect

from app.frontend import frontend


@frontend.route('/favicon.ico')
def favicon():
    return redirect('/static/favicon.png')