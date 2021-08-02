from flask import render_template, request, current_app, send_from_directory, redirect, jsonify

from app.frontend import frontend


@frontend.route('/favicon.ico')
def favicon():
    return redirect('/static/favicon.png')

@frontend.route('/')
def main():
    return jsonify({"code": 77})


@frontend.route('/simple_chat')
def simple_chat():
    return render_template('simple_chat.html')