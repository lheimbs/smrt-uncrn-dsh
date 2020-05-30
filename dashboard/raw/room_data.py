#!/usr/bin/env python3

import logging
from datetime import datetime

import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from dash.dependencies import Input, Output

from ..app import app, COLORS
from . import sql

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
                    id='raw-room-data-settings-show-hide-switch',
                    on=True,
                    color=COLORS['foreground'],
                ),
            ],
        ),
        html.Div(
            id='raw-room-data-settings-sidebar',
            className="sidebar",
            children=[
                html.Div(
                    className='card',
                    children=[
                        html.H6("Select number of entries:"),
                        dcc.Input(
                            id='raw-room-data-settings-num-results',
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
                    style={'paddingBottom': '10px'},
                    children=[
                        html.H6("Choose Daterange:"),
                        dcc.DatePickerRange(
                            id="raw-room-data-settings-date-picker",
                            start_date_placeholder_text="Start Period",
                            end_date_placeholder_text="End Period",
                            # minimum_nights=1,
                            display_format='DD MM Y',
                            month_format='MM YYYY',
                            day_size=35,
                            first_day_of_week=1,
                            persistence=True,
                            persistence_type='session',
                            updatemode='bothdates',
                            with_full_screen_portal=False,
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            id='raw-room-data-content',
            className="one_row",
            children=[
                dcc.Loading(id="raw-room-data-data-loading", type="default", color=COLORS['foreground'], children=[
                    dash_table.DataTable(
                        id='raw-room-data-data',
                        columns=[
                            {"name": 'Date', "id": 'date'},
                            {"name": 'Time', "id": 'time'},
                            {"name": 'Temperature', "id": 'temperature'},
                            {"name": 'Humidity', "id": 'humidity'},
                            {"name": 'Pressure', "id": 'pressure'},
                            {"name": 'Altitude', "id": 'altitude'},
                            {"name": 'Brightness', "id": 'brightness'},
                        ],
                        data=[],
                        page_action="native",
                        page_current=0,
                        page_size=50,
                        # fixed_rows={'headers': True},
                        style_table={'height': '75vh', 'overflowY': 'auto'},
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
                        style_data_conditional=[
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': COLORS['background-sub-medium'],
                            }
                        ],
                    ),
                ]),
            ],
        )
    ],
)


@app.callback(
    [
        Output('raw-room-data-settings-sidebar', 'style'),
        Output('raw-room-data-content', 'style'),
    ],
    [
        Input('raw-room-data-settings-show-hide-switch', 'on'),
    ],
)
def toggle_raw_room_data_sidebar(toggle_button):
    if not toggle_button:
        return {'width': '0'}, {'marginLeft': '0'}
    return {'width': '15vw'}, {'marginLeft': '15vw'}


@app.callback(
    Output('raw-room-data-data', 'data'),
    [
        Input('raw-room-data-settings-num-results', 'value'),
        Input('raw-room-data-settings-date-picker', 'start_date'),
        Input('raw-room-data-settings-date-picker', 'end_date'),
    ]
)
def get_raw_room_data(limit, start_date, end_date):
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    data = sql.get_raw_room_data(limit, start_date, end_date)
    return data.to_dict('records')
