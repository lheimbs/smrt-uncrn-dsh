#!/usr/bin/env python3

import logging
from datetime import datetime
from math import floor

import pandas as pd
import scipy.signal as signal
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
from plotly.subplots import make_subplots

from ..app import app, COLORS
from ..models.RoomData import RoomData

logger = logging.getLogger()

layout = html.Div(
    className="row one_row",
    children=[
        dcc.Store(id='data-history-settings-state'),
        html.Div(
            id='data-history-overlay',
            className="overlay",
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
                html.Hr(),
                html.Button('Show graph', id='data-history-show-data'),
            ],
        ),
        html.Button('Settings', id='data-history-show-settings'),
        html.Div(
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
        Output('data-history-settings-state', 'data'),
    ],
    [
        Input('data-history-overlay', 'loading_state'),
        Input('data-history-show-data', 'n_clicks'),
        Input('data-history-show-settings', 'n_clicks'),
    ],
    [State('data-history-settings-state', 'data')]
)
def display_data_history_overlay(state, data_clicks, hist_clicks, settings_state):
    if settings_state:
        return {'display': 'none'}, False
    return {'display': 'block'}, True


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

    if (start_date is None and end_date is None) or errors['room-data']:
        return fig

    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    data_query = RoomData.query.filter(RoomData.date.between(start_date, end_date))

    data_count = data_query.count()
    nth_row = floor(data_count / current_width) if data_count > current_width else 1
    nth_row = 60 if nth_row > 60 else nth_row

    logger.debug(f"current_width: {current_width}, data_count {data_count}, nth {nth_row}")
    data = pd.DataFrame([room_data.to_dict() for room_data in data_query.filter(RoomData.id % nth_row == 0)])

    for i, value in enumerate(chosen_values):
        # Design of Buterworth filter
        filter_order = 2    # Filter order
        cutoff_freq = 0.2   # Cutoff frequency
        B, A = signal.butter(filter_order, cutoff_freq, output='ba')

        # Apply filter
        tempf = signal.filtfilt(B, A, data[value], axis=0)

        fig.add_trace(
            go.Scatter(
                mode='lines',
                name=value,
                x=data['date'],
                y=tempf,
            ),
            row=i+1, col=1,
        )
    return fig
