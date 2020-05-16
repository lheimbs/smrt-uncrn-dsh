#!/usr/bin/env python3

import argparse
import logging

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# setup logging
parser = argparse.ArgumentParser()
parser.add_argument(
    '-d', '--debug',
    help="Print debugging statements",
    action="store_const", dest="loglevel", const=logging.DEBUG,
    default=logging.WARNING,
)
parser.add_argument(
    '-v', '--verbose',
    help="Be verbose",
    action="store_const", dest="loglevel", const=logging.INFO,
)
args = parser.parse_args()
logging.basicConfig(
    format="%(module)15s - %(levelname)-8s : %(message)s",
    level=args.loglevel
)
logger = logging.getLogger()
logger.debug('index - debug')
logger.info('index - info')
logger.warning('index - warning')


# page import here, to get the supplied log level in modules
from app import app                 # noqa: E402
from general import general       # noqa: E402
from data import data       # noqa: E402
from mqtt import mqtt       # noqa: E402
from shopping import shopping       # noqa: E402


app.layout = html.Div(
    className="app__container",
    children=[
        # store site's settings
        # dcc.Store(id='local', storage_type='local'),
        dcc.Tabs(
            id="main-tabs",
            value="data-tab",
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
            className="app__tab__content"
        ),
    ],
)


@app.callback(Output('main-tabs-content', 'children'),
              [Input('main-tabs', 'value')])
def render_main_content(tab):
    if tab == 'general-tab':
        layout = general.layout
    elif tab == 'data-tab':
        layout = data.layout
    elif tab == 'mqtt-tab':
        layout = mqtt.layout
    else:
        layout = shopping.layout
    return layout


if __name__ == "__main__":
    app.run_server(debug=True, port=5002, host='0.0.0.0', threaded=True)
