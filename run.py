from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from app import create_app
from app.extensions import db

app = create_app()

manager = Manager(app)

migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)


@manager.command
def runserver():
    app.run()


if __name__ == '__main__':
    manager.run()