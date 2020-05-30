#!/usr/bin/env python3

import logging

import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from dash.dependencies import Input, Output

from dashboard.app import app, COLORS
from .. import sql

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
                    id='raw-shopping-items-settings-show-hide-switch',
                    on=True,
                    color=COLORS['foreground'],
                ),
            ],
        ),
        html.Div(
            id='raw-shopping-items-settings-sidebar',
            className="sidebar",
            children=[
                html.Div(
                    className='card',
                    children=[
                        html.H6("Select number of entries:"),
                        dcc.Input(
                            id='raw-shopping-items-settings-num-results',
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
                        html.H6("Search Items:"),
                        dcc.Input(
                            id="raw-shopping-items-settings-search",
                            type='text',
                            debounce=True,
                        )
                    ],
                ),
            ],
        ),
        html.Div(
            id='raw-shopping-items-content',
            className="one_row",
            children=[
                dcc.Loading(
                    id="raw-shopping-items-data-loading",
                    type="default", color=COLORS['foreground'],
                    children=[
                        dash_table.DataTable(
                            id='raw-shopping-items-data',
                            columns=[
                                {"name": 'Name', "id": 'name'},
                                {"name": 'Price', "id": 'price'},
                                {"name": 'Price per Volume', "id": 'price_per_volume'},
                                {"name": 'Volume', "id": 'volume'},
                                {"name": 'Sale', "id": 'sale'},
                                {"name": 'Note', "id": 'note'},
                                {"name": 'Category', "id": 'category'},
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
                    ]
                ),
            ],
        )
    ],
)


@app.callback(
    [
        Output('raw-shopping-items-settings-sidebar', 'style'),
        Output('raw-shopping-items-content', 'style'),
    ],
    [
        Input('raw-shopping-items-settings-show-hide-switch', 'on'),
    ],
)
def toggle_raw_room_data_sidebar(toggle_button):
    if not toggle_button:
        return {'width': '0'}, {'marginLeft': '0'}
    return {'width': '15vw'}, {'marginLeft': '15vw'}


@app.callback(
    Output('raw-shopping-items-data', 'data'),
    [
        Input('raw-shopping-items-settings-num-results', 'value'),
        Input('raw-shopping-items-settings-search', 'value'),
    ]
)
def get_raw_room_data(limit, search):
    data = sql.get_raw_shopping_items(limit, search)
    return data.to_dict('records')
