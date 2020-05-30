#!/usr/bin/env python3

import logging

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from ..app import app
from . import mqtt
from . import shopping
from . import rf_data
from . import room_data
from . import probes

logger = logging.getLogger()

layout = html.Div([
    dcc.Tabs(
        id="raw-main-tabs",
        persistence=True,
        parent_className='custom__main__tabs',
        className='custom__main__tabs__container',
        children=[
            dcc.Tab(
                label="MQTT",
                value="raw-mqtt-tab",
                className='custom__main__sub__tab',
                selected_className='custom__main__sub__tab____selected',
            ),
            dcc.Tab(
                label="Room Data",
                value="raw-room-data-tab",
                className='custom__main__sub__tab',
                selected_className='custom__main__sub__tab____selected',
            ),
            dcc.Tab(
                label="Shopping",
                value="raw-shopping-tab",
                className='custom__main__sub__tab',
                selected_className='custom__main__sub__tab____selected',
            ),
            dcc.Tab(
                label="Probe Requests",
                value="raw-probes-data-tab",
                className='custom__main__sub__tab',
                selected_className='custom__main__sub__tab____selected',
            ),
            dcc.Tab(
                label="Rf Data",
                value="raw-rf-data-tab",
                className='custom__main__sub__tab',
                selected_className='custom__main__sub__tab____selected',
            ),
        ]
    ),
    html.Div(
        id="raw-tabs-content",
        className="app__tab__content"
    ),
])


@app.callback(Output('raw-tabs-content', 'children'),
              [Input('raw-main-tabs', 'value')])
def render_shopping_content(tab):
    logger.debug(f"'render_shopping_tab' called with tab '{tab}'.'")
    if tab == 'raw-mqtt-tab':
        layout = mqtt.layout
    elif tab == 'raw-shopping-tab':
        layout = shopping.layout
    elif tab == 'raw-room-data-tab':
        layout = room_data.layout
    elif tab == 'raw-probes-data-tab':
        layout = probes.layout
    elif tab == 'raw-rf-data-tab':
        layout = rf_data.layout
    else:
        layout = mqtt.layout
    return layout
