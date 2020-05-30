#!/usr/bin/env python3

import logging
# from datetime import datetime

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
# from sqlalchemy import exc

from .app import app  # , db, server
from . import shopping
from . import general
from . import data
from . import raw
# from models.Shopping import List, Shop, Category, Item
from .misc.precheck_errors import precheck_errors

logger = logging.getLogger()
# errors, errors_dict = precheck_errors()

layout = html.Div(
    className="wrapper",
    children=[
        # store site's settings
        dcc.Store(id='error-store', storage_type='local'),
        html.Div(
            className='content',
            children=[
                dcc.Tabs(
                    persistence=True,
                    id="main-tabs",
                    parent_className='custom__main__tabs',
                    className='custom__main__tabs__container',
                    children=[
                        dcc.Tab(
                            label="Data",
                            value="data-tab",
                            className='custom__main__tab',
                            selected_className='custom__main__tab____selected',
                        ),
                        dcc.Tab(
                            label="Shopping",
                            value="shopping-tab",
                            className='custom__main__tab',
                            selected_className='custom__main__tab____selected',
                        ),
                        dcc.Tab(
                            label="System",
                            value="system-tab",
                            className='custom__main__tab',
                            selected_className='custom__main__tab____selected',
                        ),
                        dcc.Tab(
                            label="RAW",
                            value="raw-tab",
                            className='custom__main__tab',
                            selected_className='custom__main__tab____selected',
                        ),
                    ]
                ),
                html.Div(
                    id="main-tabs-content",
                    className="content"
                ),
            ],
        ),
        html.Footer(
            id='errors-footer',
            className='errors-div footer',
            children=[error for error in precheck_errors()[0]],
        ),
    ],
)


@app.callback(
    Output('main-tabs-content', 'children'),
    [Input('main-tabs', 'value')],
)
def render_main_content(tab):
    if tab == 'system-tab':
        layout = general.layout
    elif tab == 'data-tab':
        layout = data.layout
    elif tab == 'raw-tab':
        layout = raw.layout
    elif tab == 'shopping-tab':
        layout = shopping.layout
    else:
        layout = data.layout
    return layout


@app.callback(
    Output('error-store', 'data'),
    [Input('main-tabs', 'loading_state')]
)
def update_error_store(_):
    return precheck_errors()[1]


if __name__ == "__main__":
    '''
    logger.info(f"Environment: {server.config['ENV']}")
    logger.info(f"Debug: {server.config['DEBUG']}")
    logger.info(f"Secret key: {server.config['SECRET_KEY']}")

    if server.config['DEBUG']:
        generate_shopping_data()
    '''

    app.layout = layout
    app.run_server(debug=True, port=5002, host='0.0.0.0', threaded=True)
    # Deleted 'self.logger.setLevel' from dash.py so debug messages are getting logged in callbacks
    # logging.getLogger('werkzeug').setLevel(logging.ERROR)
    # app.logger.setLevel(logging.Debug)
