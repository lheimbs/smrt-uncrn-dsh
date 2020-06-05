#!/usr/bin/env python3

import logging
from datetime import datetime

import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from dash.dependencies import Input, Output, State

from ..app import app, COLORS
from .sql import (
    get_mqtt_topics_as_options,
    get_mqtt_messages_by_topic,
)

logger = logging.getLogger()

layout = html.Div(
    className="row one_row",
    children=[
        html.Div(
            className='settings_open_close row',
            style={'marginTop': '5px'},
            children=[
                html.P('Settings:', className='one column', style={'marginTop': '5px', 'marginBottom': '0px'}),
                daq.BooleanSwitch(
                    className='one column',
                    id='raw-mqtt-settings-show-hide-switch',
                    on=True,
                    color=COLORS['foreground'],
                ),
            ],
        ),
        html.Div(
            id='raw-mqtt-settings-sidebar',
            className="sidebar",
            children=[
                html.Div(
                    className='card',
                    children=[
                        html.H6("Select number of entries:"),
                        dcc.Input(
                            id='raw-mqtt-settings-num-results',
                            type='number',
                            value=1000,
                            min=1,
                            max=99999,
                            debounce=True,
                        )
                    ]
                ),
                html.Div(
                    className='card',
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
                    ]
                ),
                html.Div(
                    className='card',
                    style={'paddingBottom': '10px'},
                    children=[
                        html.H6("Choose Daterange:"),
                        dcc.DatePickerRange(
                            id="raw-mqtt-settings-date-picker",
                            start_date_placeholder_text="Start Period",
                            end_date_placeholder_text="End Period",
                            # minimum_nights=1,
                            display_format='DD MM Y',
                            month_format='MM YYYY',
                            day_size=35,
                            first_day_of_week=1,
                            updatemode='bothdates',
                            with_full_screen_portal=False,
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            id='raw-mqtt-content',
            className="one_row",
            children=[
                dcc.Loading(id="loading-mqtt-messages", type="default", color=COLORS['foreground'], children=[
                    dash_table.DataTable(
                        id='raw-mqtt-data',
                        columns=[
                            {"name": 'Date', "id": 'date'},
                            {"name": 'Time', "id": 'time'},
                            {"name": 'Topic', "id": 'topic'},
                            {"name": 'Payload', "id": 'payload'},
                            {"name": 'Retain', "id": 'retain'},
                        ],
                        data=[],
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
            ]
        )
    ],
)


@app.callback(
    [
        Output('raw-mqtt-settings-sidebar', 'style'),
        Output('raw-mqtt-content', 'style'),
    ],
    [
        Input('raw-mqtt-settings-show-hide-switch', 'on'),
    ],
)
def toggle_raw_room_data_sidebar(toggle_button):
    if not toggle_button:
        return {'width': '0'}, {'marginLeft': '0'}
    return {'width': '15vw'}, {'marginLeft': '15vw'}


@app.callback(
    Output('mqtt-select-topics', 'options'),
    [Input('mqtt-select-topics', 'loading_state')],
    [State('error-store', 'data')]
)
def mqtt_topics_as_options(_, errors):
    if errors['mqtt_messages']:
        logger.warning("Mqtt-Messages table does not exist. Cant fetch mqtt topics.")
        return []
    return get_mqtt_topics_as_options()


@app.callback(
    Output('raw-mqtt-data', 'data'),
    [
        Input('mqtt-select-topics', 'value'),
        Input('raw-mqtt-settings-num-results', 'value'),
        Input('raw-mqtt-settings-date-picker', 'start_date'),
        Input('raw-mqtt-settings-date-picker', 'end_date'),
    ]
)
def get_table_data(selected_topics, limit, start_date, end_date):
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    data = get_mqtt_messages_by_topic(selected_topics, limit, start_date, end_date)
    return data.to_dict('records')
