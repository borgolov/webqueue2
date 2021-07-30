# -*- coding: utf-8 -*-
from flask import Flask, render_template
from .extensions import db, migrate, ma, socket_io
from app import methods, models
from .frontend import frontend
from .api import restful_api

__all__ = ['create_app']

BLUEPRINTS = (frontend, restful_api, )


def create_app(config=None, app_name='app', blueprints=None):
    """Create a Flask app."""

    app = Flask(app_name)
    configure_app(app, config)
    configure_extensions(app)
    register_blueprints(app, blueprints)
    configure_logging(app)
    configure_template_filters(app)
    configure_error_handlers(app)

    return app


def configure_app(app, config=None):
    """Different ways of configurations."""

    if config:
        app.config.from_json(config, silent=True)
    else:
        app.config.from_json('settings.json', silent=True)


def configure_extensions(app):

    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    socket_io.init_app(app)


def register_blueprints(app, blueprints):
    """Configure blueprints in views."""

    for bp in blueprints or BLUEPRINTS:
        app.register_blueprint(bp)


def configure_template_filters(app):
    """Configure filters."""
    pass


def configure_logging(app):
    """Configure file(info) and email(error) logging."""

    #if app.debug or app.testing:
        # Skip debug and test mode. Just check standard output.
    #    return

    import logging
    import os
    from logging.handlers import SMTPHandler

    # Set info level on logger, which might be overwritten by handers.
    # Suppress DEBUG messages.
    app.logger.setLevel(logging.INFO)

    info_log = os.path.join(app.config['LOG_FOLDER'], 'info.log')
    info_file_handler = logging.handlers.RotatingFileHandler(info_log, maxBytes=100000, backupCount=10)
    info_file_handler.setLevel(logging.INFO)
    info_file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]')
    )
    app.logger.addHandler(info_file_handler)

    # Testing
    #app.logger.info("testing info.")
    #app.logger.warn("testing warn.")
    #app.logger.error("testing error.")


def configure_error_handlers(app):

    @app.errorhandler(403)
    def forbidden_page(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return render_template("errors/405.html"), 404

    @app.errorhandler(500)
    def server_error_page(error):
        return render_template("errors/500.html"), 500
