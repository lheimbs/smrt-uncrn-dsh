#!/usr/bin/env python3

import logging
from datetime import datetime

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# page import here, to get the supplied log level in modules (# noqa E420?)
from .app import app, db, server
from . import shopping
from . import general
from . import data
from . import mqtt
from models.Shopping import List, Shop, Category, Item

logger = logging.getLogger()


def generate_shopping_data():
    cat = Category(name='Lebensmittel')
    shop = Shop(name='REWE', category=cat)
    items = [
        Item(name='Bier', price=1.09, volume='', price_per_volume='', sale=False, note=''),
        Item(name='Pfand', price=0.08, volume='', price_per_volume='', sale=False, note=''),
        Item(name='Leergut', price=0.08, volume='', price_per_volume='', sale=False, note=''),
        Item(name='Kinder Bueno', price=1.99, volume='', price_per_volume='', sale=True, note=''),
        Item(name='Schokobons', price=1.99, volume='200g', price_per_volume='', sale=False, note=''),
        Item(name='Eis Stiel-Brownie', price=1.69, volume='', price_per_volume='', sale=False, note=''),
    ]
    list_1 = List(date=datetime(2020, 5, 16, 0, 0), price=6.76, shop=shop, items=items)

    list_2 = List(date=datetime(2019, 5, 15, 0, 0), price=3.61, shop=Shop(name='EDEKA', category=cat), items=[
        Item(name='Toast', price=0.59, volume='', price_per_volume='', sale=False, note=''),
        Item(name='Schokobons klein', price=1.99, volume='', price_per_volume='', sale=False, note=''),
        Item(name='Joghurt', price=0.88, volume='', price_per_volume='', sale=False, note='0,15'),
        Item(name='Pfand', price=0.15, volume='', price_per_volume='', sale=False, note='')
    ])

    db.session.add(list_1)
    db.session.add(list_2)
    db.session.commit()


def precheck_errors():
    tables = ['room-data', 'rf-data', 'mqtt-message', 'list', 'item', 'shop', 'category']
    errors_str = []
    errors_dict = {
        'database': False,
        'database-probes': False,
    }
    try:
        db.session.execute("SELECT 1")
    except Exception as exc:
        logger.warning("Database not found.")
        logger.debug(exc)
        errors_str.append("ERROR: Database not found.")
        errors_dict['database'] = True
    try:
        db.session.execute("SELECT 1", bind=db.get_engine(server, 'probe-requests'))
    except Exception as exc:
        logger.warning("Database for Probe-Requests not found.")
        logger.debug(exc)
        errors_str.append("ERROR: Database for Probe-Requests not found.")
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
    logger.info(f"Environment: {server.config['ENV']}")
    logger.info(f"Debug: {server.config['DEBUG']}")
    logger.info(f"Secret key: {server.config['SECRET_KEY']}")

    if server.config['DEBUG']:
        generate_shopping_data()

    app.layout = layout
    app.run_server(debug=True, port=5002, host='0.0.0.0', threaded=True)
    # Deleted 'self.logger.setLevel' from dash.py so debug messages are getting logged in callbacks
    # logging.getLogger('werkzeug').setLevel(logging.ERROR)
    # app.logger.setLevel(logging.Debug)
