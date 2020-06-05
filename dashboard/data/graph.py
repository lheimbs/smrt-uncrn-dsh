#!/usr/bin/env python3

import logging
from datetime import datetime
from math import floor

import pandas as pd
import scipy.signal as signal
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
from plotly.subplots import make_subplots

from ..app import app, COLORS
from models.RoomData import RoomData

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
                    id='data-history-show-hide-switch',
                    on=True,
                    color=COLORS['foreground'],
                ),
            ],
        ),
        html.Div(
            id='data-history-overlay',
            className="sidebar",
            children=[
                html.Div(
                    className='card',
                    children=[
                        html.H6("Choose display data:"),
                        dcc.Checklist(
                            id="data-history-values",
                            options=[
                                {'label': 'Temperature', 'value': 'temperature'},
                                {'label': 'Humidity', 'value': 'humidity'},
                                {'label': 'Pressure', 'value': 'pressure'},
                                {'label': 'Altitude', 'value': 'altitude', 'disabled': False},
                                {'label': 'Brightness', 'value': 'brightness'},
                            ],
                            value=['temperature', 'humidity', 'pressure'],
                            labelStyle={'display': 'block'},
                            persistence_type='memory',
                            className='checklist',
                        ),
                    ]
                ),
                html.Div(
                    className='card',
                    style={'paddingBottom': '10px'},
                    children=[
                        html.H6("Choose Daterange:"),
                        dcc.DatePickerRange(
                            id="data-history-date-picker",
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
                            with_full_screen_portal=True,
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            id='data-hist-sidebar-content',
            className="one_row",
            children=[
                dcc.Store(id='data-history-graph-current-width'),
                dcc.Loading(id="loading-1", color=COLORS['foreground'], children=[
                    dcc.Graph(
                        style={'height': '80vh'},
                        id="data-history-graph",
                        config={
                            'staticPlot': False,
                            'showSendToCloud': False,
                            'showLink': False,
                            'displaylogo': False,
                            'modeBarButtonsToRemove':
                            [
                                'sendDataToCloud',
                                'hoverClosestCartesian',
                                'hoverCompareCartesian',
                                'zoom3d',
                                'pan3d',
                                'orbitRotation',
                                'tableRotation',
                                'handleDrag3d',
                                'resetCameraDefault3d',
                                'resetCameraLastSave3d',
                                'hoverClosest3d',
                                'zoomInGeo',
                                'zoomOutGeo',
                                'resetGeo',
                                'hoverClosestGeo',
                                'hoverClosestGl2d',
                                'hoverClosestPie',
                                'toggleSpikelines',
                                'toImage'
                            ],
                        },
                        className="graph",
                    )
                ], type="default"),
            ],
        )
    ],
)


@app.callback(
    [
        Output('data-history-overlay', 'style'),
        Output('data-hist-sidebar-content', 'style'),
    ],
    [
        Input('data-history-overlay', 'loading_state'),
        Input('data-history-show-hide-switch', 'on'),
    ],
)
def display_data_history_overlay(state, toggle_button):
    if not toggle_button:
        return {'width': '0'}, {'marginLeft': '0'}
    return {'width': '15vw'}, {'marginLeft': '15vw'}


app.clientside_callback(
    '''
    window.onload = function getGraphWidth() {
        if(!document.getElementById("data-history-graph")) {
            width = 0;
        }
        else {
            var width = document.getElementById("data-history-graph").clientWidth;
        }
        return width;
    };
    ''',
    Output('data-history-graph-current-width', 'data'),
    [Input('data-history-graph', 'loading_state')]
)


@app.callback(
    Output('data-history-graph', 'figure'),
    [
        Input('data-history-date-picker', 'start_date'),
        Input('data-history-date-picker', 'end_date'),
        Input('data-history-values', 'value'),
        Input('data-history-graph-current-width', 'data')
    ],
    [State('error-store', 'data')],
)
def update_history_graph(start_date, end_date, chosen_values, current_width, errors):
    n_chosen = len(chosen_values) if len(chosen_values) else 1
    fig = make_subplots(
        rows=n_chosen,
        cols=1,
    )
    fig.update_layout({
        'autosize': True,
        'coloraxis': {
            'colorbar': {
                'outlinewidth': 0,
                'bordercolor': COLORS['background'],
                'bgcolor': COLORS['background'],
            },
        },
        'colorway': COLORS['colorway'],
        'font': {
            'color': COLORS['foreground'],
        },
        'legend': {
            'orientation': 'h',
        },
        'margin': {
            'l': 10, 'r': 10, 't': 20, 'b': 10, 'pad': 0,
        },
        'paper_bgcolor': COLORS['background'],
        'plot_bgcolor': COLORS['background'],
        'xaxis': {
            'gridcolor': COLORS['dark-2'],
            'showline': True, 'linewidth': 1,
            'linecolor': COLORS['border-medium'],
            'showgrid': True, 'gridwidth': 1,
            'zeroline': True, 'zerolinewidth': 1,
            'zerolinecolor': COLORS['border-medium'],
        },
        'xaxis2': {
            'gridcolor': COLORS['dark-2'],
            'showline': True, 'linewidth': 1,
            'linecolor': COLORS['border-medium'],
            'showgrid': True, 'gridwidth': 1,
            'zeroline': True, 'zerolinewidth': 1,
            'zerolinecolor': COLORS['border-medium'],
        },
        'xaxis3': {
            'gridcolor': COLORS['dark-2'],
            'showline': True, 'linewidth': 1,
            'linecolor': COLORS['border-medium'],
            'showgrid': True, 'gridwidth': 1,
            'zeroline': True, 'zerolinewidth': 1,
            'zerolinecolor': COLORS['border-medium'],
        },
        'xaxis4': {
            'gridcolor': COLORS['dark-2'],
            'showline': True, 'linewidth': 1,
            'linecolor': COLORS['border-medium'],
            'showgrid': True, 'gridwidth': 1,
            'zeroline': True, 'zerolinewidth': 1,
            'zerolinecolor': COLORS['border-medium'],
        },
        'xaxis5': {
            'gridcolor': COLORS['dark-2'],
            'showline': True, 'linewidth': 1,
            'linecolor': COLORS['border-medium'],
            'showgrid': True, 'gridwidth': 1,
            'zeroline': True, 'zerolinewidth': 1,
            'zerolinecolor': COLORS['border-medium'],
        },
        'yaxis': {
            'gridcolor': COLORS['dark-2'],
            'showline': True, 'linewidth': 1,
            'linecolor': COLORS['border-medium'],
            'showgrid': True, 'gridwidth': 1,
            'zeroline': True, 'zerolinewidth': 1,
            'zerolinecolor': COLORS['border-medium'],
        },
        'yaxis2': {
            'gridcolor': COLORS['dark-2'],
            'showline': True, 'linewidth': 1,
            'linecolor': COLORS['border-medium'],
            'showgrid': True, 'gridwidth': 1,
            'zeroline': True, 'zerolinewidth': 1,
            'zerolinecolor': COLORS['border-medium'],
        },
        'yaxis3': {
            'gridcolor': COLORS['dark-2'],
            'showline': True, 'linewidth': 1,
            'linecolor': COLORS['border-medium'],
            'showgrid': True, 'gridwidth': 1,
            'zeroline': True, 'zerolinewidth': 1,
            'zerolinecolor': COLORS['border-medium'],
        },
        'yaxis4': {
            'gridcolor': COLORS['dark-2'],
            'showline': True, 'linewidth': 1,
            'linecolor': COLORS['border-medium'],
            'showgrid': True, 'gridwidth': 1,
            'zeroline': True, 'zerolinewidth': 1,
            'zerolinecolor': COLORS['border-medium'],
        },
        'yaxis5': {
            'gridcolor': COLORS['dark-2'],
            'showline': True, 'linewidth': 1,
            'linecolor': COLORS['border-medium'],
            'showgrid': True, 'gridwidth': 1,
            'zeroline': True, 'zerolinewidth': 1,
            'zerolinecolor': COLORS['border-medium'],
        }
    })
    if current_width:
        current_width = (current_width / 2) if current_width > 0 else 1
    else:
        current_width = 1

    if (start_date is None and end_date is None) or errors['room_data']:
        return fig

    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    data_query = RoomData.query.filter(RoomData.date.between(start_date, end_date))

    data_count = data_query.count()
    if not data_count:
        return fig

    nth_row = floor(data_count / current_width) if data_count > current_width else 1
    nth_row = 60 if nth_row > 60 else nth_row

    logger.debug(f"current_width: {current_width}, data_count {data_count}, nth {nth_row}")
    data = pd.DataFrame([room_data.to_dict() for room_data in data_query.filter(RoomData.id % nth_row == 0)])

    for i, value in enumerate(chosen_values):
        if data[value].count() > 10:
            # Design of Buterworth filter
            filter_order = 2    # Filter order
            cutoff_freq = 0.2   # Cutoff frequency
            B, A = signal.butter(filter_order, cutoff_freq, output='ba')

            # Apply filter
            tempf = signal.filtfilt(B, A, data[value])
        else:
            tempf = data[value]

        fig.add_trace(
            go.Scatter(
                mode='lines',
                name=value,
                x=data['date'],
                y=tempf,
            ),
            row=i + 1, col=1,
        )
    return fig
