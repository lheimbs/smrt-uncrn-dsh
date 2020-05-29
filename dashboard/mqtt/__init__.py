#!/usr/bin/env python3

import logging

import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from ..app import app, COLORS
from .sql import (
    get_mqtt_topics_as_options,
    get_mqtt_messages_by_topic,
)

logger = logging.getLogger()

layout = html.Div([
    html.Div(
        className='row',
        children=[
            html.Div(
                className='two columns settings',
                children=[
                    html.H6("Select topics:"),
                    dcc.Loading(id="loading-mqtt-topics", color=COLORS['foreground'], children=[
                        dcc.Checklist(
                            id="mqtt-select-topics",
                            value=[],
                            labelStyle={'display': 'block'},
                            className="mqtt__topic__select",
                        ),
                    ]),
                    html.H6("Select number of entries:"),
                    dcc.Input(
                        id='mqtt-select-num-msgs',
                        type='number',
                        value=1000,
                        min=1,
                        max=99999,
                        debounce=True,
                    )
                ],
            ),
            html.Div(
                className='ten columns',
                children=[
                    dcc.Loading(id="loading-mqtt-messages", type="default", color=COLORS['foreground'], children=[
                        dash_table.DataTable(
                            id='table-mqtt-messages',
                            columns=[
                                {"name": 'Date', "id": 'date'},
                                {"name": 'Time', "id": 'time'},
                                {"name": 'Topic', "id": 'topic'},
                                {"name": 'Payload', "id": 'payload'},
                            ],
                            data=[],  # data.to_dict('records'),

                            page_action="native",
                            page_current=0,
                            page_size=25,
                            style_as_list_view=True,
                            style_header={
                                'backgroundColor': COLORS['background-medium'],
                                'fontWeight': 'bold'
                            },
                            style_cell={
                                'padding': '5px',
                                'textAlign': 'center',
                                'backgroundColor': COLORS['background'],
                            },
                        ),
                    ]),
                ],
            )
        ],
    ),
])


@app.callback(
    Output('mqtt-select-topics', 'options'),
    [Input('mqtt-select-topics', 'loading_state')],
    [State('error-store', 'data')]
)
def mqtt_topics_as_options(_, errors):
    if errors['mqtt-message']:
        logger.warning("Mqtt-Messages table does not exist. Cant fetch mqtt topics.")
        return []
    return get_mqtt_topics_as_options()


@app.callback(Output('table-mqtt-messages', 'data'),
              [Input('mqtt-select-topics', 'value'),
               Input('mqtt-select-num-msgs', 'value')])
def get_table_data(selected_topics, limit):
    if selected_topics and limit:
        logger.debug(f"MQTT Messages callback. Topics: {selected_topics}, limit: {limit}.")
        data = get_mqtt_messages_by_topic(selected_topics, limit)
        return data.to_dict('records')
    else:
        return []