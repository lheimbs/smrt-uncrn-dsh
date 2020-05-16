#!/usr/bin/env python3

import os
import logging
from math import ceil

import scipy.signal as signal
import dash_daq as daq
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app, COLORS

logger = logging.getLogger()

GRAPH_INTERVAL = os.environ.get("GRAPH_INTERVAL", 60000)
EMPTY_GRAPH = {
    'data': [{'x': [], 'y': [], }, ],
    'layout':
    {
        'backgroundColor': COLORS['background'],
        'paper_bgcolor': COLORS['background'],
        'plot_bgcolor': COLORS['background'],
        'font': {
            'color': COLORS['foreground-dark']
        },
        'margin': {'l': 30, 'b': 30, 'r': 10, 't': 30},
        # 'width': '100%',
        'height': '250',
    }
}
UNITS = {
    'temperature': '°C',
    'pressure': 'Pa',
    'humidity': '%',
    'altitude': 'm',
    'brightness': 'lx',
}
DIV_COLUMNS = {
    1: "twelve columns",
    2: "eight columns",
    3: "four columns",
    4: "three columns",
    5: "two columns",
}


layout = html.Div(
    className='row',
    children=[
        html.Div(
            children=[
                html.H6("Choose display data:"),
                dcc.Checklist(
                    id="data-overview-values",
                    options=[
                        {'label': 'Temperature', 'value': 'temperature'},
                        {'label': 'Humidity', 'value': 'humidity'},
                        {'label': 'Pressure', 'value': 'pressure'},
                        {'label': 'Altitude', 'value': 'altitude', 'disabled': True},
                        {'label': 'Brightness', 'value': 'brightness'},
                    ],
                    value=['temperature', 'humidity', 'pressure'],
                    labelStyle={'display': 'block'},
                    persistence_type='memory',
                    className='checklist',
                )
            ],
            className='two columns settings',
        ),
        html.Div(
            children=[
                html.Div(
                    id="current-data",
                    className='overview__current__gauges row',
                ),
                html.Div(
                    className='row',
                    children=[
                        html.Div(
                            className="twelve column",
                            children=[
                                html.H6("Last 24 hours", className="data__overview__day__title title__center"),
                            ],
                        ),
                        html.Div(
                            className="twelve column graph_in_column",
                            children=[
                                dcc.Graph(
                                    id="day-data-graph",
                                    figure=EMPTY_GRAPH,
                                    config={
                                        'staticPlot': True
                                    },
                                    className="graph",
                                ),
                            ],
                        ),
                    ],
                ),
                dcc.Interval(
                    id="data-overview-update",
                    interval=int(GRAPH_INTERVAL),
                    n_intervals=0,
                ),
            ],
            className='ten columns data',
        )
    ],
)


@app.callback(Output('current-data', 'children'),
              [Input('data-overview-update', 'n_intervals'),
               Input('data-overview-values', 'value')])
def update_current_data(interval, overview_values):
    gauges = []
    for value in overview_values:
        min_val, max_val, last = sql_data.get_gauge_data(value)
        min_val = round(min_val)
        max_val = ceil(max_val)
        step = round((max_val - min_val) / 3)

        if value in UNITS.keys():
            unit = UNITS[value]
        else:
            unit = ''

        gauges.append(
            html.Div(
                children=[
                    daq.Gauge(
                        id="current-temp-gauge",
                        label=value.capitalize(),
                        size=150,
                        value=last,
                        min=min_val,
                        max=max_val,
                        showCurrentValue=True,
                        units=unit,
                        color={
                            "gradient": True,
                            "ranges": {
                                "blue": [min_val, min_val + step],
                                "green": [min_val + step, max_val - step],
                                "red": [max_val - step, max_val]
                            }
                        },
                    )
                ],
                className=DIV_COLUMNS[len(overview_values)],
            )
        )
    return gauges


@app.callback(Output('day-data-graph', 'figure'),
              [Input('data-overview-update', 'n_intervals'),
               Input('data-overview-values', 'value')])
def update_day_graph(interval, overview_values):
    day_data = sql_data.get_day_temp()
    day_data = day_data.sort_values('datetime')

    # Design of Buterworth filter
    filter_order = 2    # Filter order
    cutoff_freq = 0.2   # Cutoff frequency
    B, A = signal.butter(filter_order, cutoff_freq, output='ba')

    # Apply filter
    tempf = signal.filtfilt(B, A, day_data['temperature'])

    return {
        'data': [
            {
                'x': day_data['datetime'],
                'y': tempf,
                'type': 'scatter',
                'name': 'Data',
                'mode': 'lines'
            },
        ],
        'layout':
        {
            'autosize': True,
            'backgroundColor': COLORS['background'],
            'paper_bgcolor': COLORS['background'],
            'plot_bgcolor': COLORS['background'],
            'font': {
                'color': COLORS['foreground-dark']
            },
            'margin': {'l': 30, 'b': 30, 'r': 10, 't': 10},
            # 'width': '100%',
            'height': '400',
        }
    }
