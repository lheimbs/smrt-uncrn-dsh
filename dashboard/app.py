#!/usr/bin/env python3

import logging
import dash
from flask import Flask

logger = logging.getLogger()

# FLASK SETUP
server = Flask(__name__, static_folder='static')
server.logger = logger

# DASH SETUP
app = dash.Dash(
    name='Smrt Uncrn Dsh',
    server=server,
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
    'border-light': '#d6d6d6',
    'border-medium': '#333333',
    'border-dark': '#0f0f0f',
    'dark-1': '#222222',
    'dark-2': '#333333',
    'red': 'red',
    'green': 'green',
    'error': '#960c0c',
    'success': '#17960c',
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
