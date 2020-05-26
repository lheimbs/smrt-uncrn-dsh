#!/usr/bin/env python3

import os
import logging

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# page import here, to get the supplied log level in modules (# noqa E420?)
from .app import app, db, DATABASE_PATH, DATABASE_PROBES_PATH
from . import shopping
from . import general
from . import data
from . import mqtt
# from .shopping 

logger = logging.getLogger()


def precheck_errors():
    tables = ['room-data', 'rf-data', 'mqtt-message', 'probe-request', 'list', 'item', 'shop', 'category']
    errors_str = []
    errors_dict = {
        'database': False,
        'database-probes': False,
    }
    if not os.path.exists(DATABASE_PATH):
        logger.warning(f"Database not found under '{DATABASE_PATH}.")
        errors_str.append(f"ERROR: Database not found under '{DATABASE_PATH}.")
        errors_dict['database'] = True
    if not os.path.exists(DATABASE_PROBES_PATH):
        logger.warning(f"Database not found under '{DATABASE_PROBES_PATH}.")
        errors_str.append(f"ERROR: Database for Probe Requests not found under '{DATABASE_PROBES_PATH}.")
        errors_dict['database-probes'] = True
    for table in tables:
        if db.engine.has_table(table):
            errors_dict[table] = False
        else:
            logger.warning(f"Table {table} not found in database.")
            errors_str.append(f"ERROR: Table {table} not found in database.")
            errors_dict.update({table: True})
    return errors_str, errors_dict


errors, errors_dict = precheck_errors()

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
                            label="General",
                            value="general-tab",
                            className='custom__main__tab',
                            selected_className='custom__main__tab____selected',
                        ),
                        dcc.Tab(
                            label="Data",
                            value="data-tab",
                            className='custom__main__tab',
                            selected_className='custom__main__tab____selected',
                        ),
                        dcc.Tab(
                            label="MQTT",
                            value="mqtt-tab",
                            className='custom__main__tab',
                            selected_className='custom__main__tab____selected',
                        ),
                        dcc.Tab(
                            label="Shopping",
                            value="shopping-tab",
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
            children=[] if not errors else [html.P(error) for error in errors],
        ),
    ],
)


@app.callback(
    Output('main-tabs-content', 'children'),
    [Input('main-tabs', 'value')],
)
def render_main_content(tab):
    if tab == 'general-tab':
        layout = general.layout
    elif tab == 'data-tab':
        layout = data.layout
    elif tab == 'mqtt-tab':
        layout = mqtt.layout
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
    return errors_dict


if __name__ == "__main__":
    app.layout = layout
    app.run_server(debug=True, port=5002, host='0.0.0.0', threaded=True)
    # Deleted 'self.logger.setLevel' from dash.py so debug messages are getting logged in callbacks
    # logging.getLogger('werkzeug').setLevel(logging.ERROR)
    # app.logger.setLevel(logging.Debug)
