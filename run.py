from flask_migrate import Migrate

from app import create_app
from app.extensions import db, socket_io

app = create_app()

migrate = Migrate(app, db)



if __name__ == '__main__':
    socket_io.run(app)