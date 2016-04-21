import flask
import flask_sqlalchemy
from flask_socketio import SocketIO

app = flask.Flask(__name__)
app.config.from_pyfile('settings.py')
db = flask_sqlalchemy.SQLAlchemy(app)

socketio = SocketIO(app)

recip_sockets = {}
