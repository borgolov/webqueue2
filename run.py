#from flask_migrate import Migrate
from threading import Thread
from app import create_app
from app.extensions import db, socket_io
from app.utils import clear_queue_on_time

app = create_app()
#migrate = Migrate(app, db)


thread = Thread(target=clear_queue_on_time)
thread.start()

if __name__ == '__main__':
    socket_io.run(app, host='0.0.0.0', port=5000)