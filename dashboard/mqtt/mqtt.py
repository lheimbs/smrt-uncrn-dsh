#!/usr/bin/env python3

import logging

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
import mqtt.messages
import mqtt.live

logger = logging.getLogger()

layout = html.Div([
    dcc.Tabs(
        id="mqtt-main-tabs",
        persistence=True,
        # value="mqtt-messages-tab",
        parent_className='custom__main__tabs',
        className='custom__main__tabs__container',
        children=[
            dcc.Tab(
                label="Messages",
                value="mqtt-messages-tab",
                className='custom__main__sub__tab',
                selected_className='custom__main__sub__tab____selected',
            ),
            dcc.Tab(
                label="Live",
                value="mqtt-live-tab",
                className='custom__main__sub__tab',
                selected_className='custom__main__sub__tab____selected',
            ),
        ]
    ),
    html.Div(
        id="mqtt-tabs-content",
        className="app__tab__content"
    ),
])


@app.callback(Output('mqtt-tabs-content', 'children'),
              [Input('mqtt-main-tabs', 'value')])
def render_mqtt_content(tab):
    if tab == 'mqtt-messages-tab':
        layout = mqtt.messages.layout
    elif tab == 'mqtt-live-tab':
        layout = mqtt.live.layout
    elif tab == 'mqtt-settings-tab':
        layout = html.Div("Settings")
    else:
        layout = mqtt.messages.layout
    return layout
