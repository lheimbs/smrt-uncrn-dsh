#!/usr/bin/env python3

import logging
import dash
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from werkzeug.utils import import_string
from flask_migrate import Migrate

logger = logging.getLogger()

external_scripts = [
    # 'https://raw.githubusercontent.com/kimmobrunfeldt/progressbar.js/master/dist/progressbar.min.js',
]

# FLASK SETUP
server = Flask(__name__, static_folder='static')

if server.config['ENV'] == 'development':
    cfg = import_string('config.config.DevelopmentConfig')()
elif server.config['ENV'] == 'testing':
    cfg = import_string('config.config.TestingConfig')()
else:
    cfg = import_string('config.config.ProductionConfig')()
server.config.from_object(cfg)
# server.config.from_pyfile('config/config.py')
# server.config.from_envvar('APP_CONFIG_FILE')

# server.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
# server.config['SQLALCHEMY_BINDS'] = {
#     'probe-requests': f'sqlite:///probe_requests.db'
# }
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
server.logger = logger

db = SQLAlchemy(server)
from models.RoomData import RoomData                       # noqa E402
from models.Shopping import Shop, List, Item, Category     # noqa E402
from models.RfData import RfData                           # noqa E402
from models.ProbeRequest import ProbeRequest               # noqa E402
from models.Mqtt import Mqtt                               # noqa E402
from models.State import State                             # noqa E402
from models.Tablet import TabletBattery                    # noqa E402
migrate = Migrate(server, db)

if server.config['ENV'] == 'development':
    # db.drop_all()
    db.create_all()

# DASH SETUP
app = dash.Dash(
    name='Smrt Uncrn Dsh',
    server=server,
    external_scripts=external_scripts,
    # routes_pathname_prefix='/graph/'
)
app.logger = logger
app.title = "Smrt Uncrn Dsh"
app.config['suppress_callback_exceptions'] = True

COLORS = {
    'foreground': '#7FDBFF',  # 4491ed',
    'foreground-dark': '#123456',
    'background': '#111111',
    'background-medium': '#252525',
    'background-sub-medium': '#1c1c1c',
    'border-light': '#d6d6d6',
    'border-medium': '#333333',
    'border-dark': '#0f0f0f',
    'dark-1': '#222222',
    'dark-2': '#333333',
    'red': 'red',
    'green': 'green',
    'error': '#960c0c',
    'success': '#17960c',
    'warning': '#f7b731',
    'colorway': [
        '#fc5c65',
        '#26de81',
        '#fd9644',
        '#2bcbba',
        '#a55eea',
        '#bff739',
        '#45aaf2',
        '#fed330',
        '#4b7bec',
        '#778ca3',
        '#eb3b5a',
        '#2d98da',
        '#fa8231',
        '#3867d6',
        '#f7b731',
        '#8854d0',
        '#20bf6b',
        '#a5b1c2',
        '#0fb9b1',
        '#4b6584',
    ]
}
