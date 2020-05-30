#!/usr/bin/env python3

import os
import logging
from datetime import datetime
from math import ceil, floor
from dateutil.relativedelta import relativedelta

import pandas as pd
import scipy.signal as signal
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State, ClientsideFunction

from . import sql
from ..app import app, COLORS

logger = logging.getLogger()

GRAPH_INTERVAL = os.environ.get("GRAPH_INTERVAL", 60000)
UNITS = {
    'temperature': '°C',
    'pressure': 'hPa',
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
        dcc.Interval(
            id="data-overview-update",
            interval=int(GRAPH_INTERVAL),
            n_intervals=0,
        ),
        dcc.Store(id='temperature_store'),
        dcc.Store(id='humidity_store'),
        dcc.Store(id='pressure_store'),
        dcc.Store(id='last_entry'),
        dcc.Store(id='last_24_hrs'),

        html.Div(
            className='row card_row',
            children=[
                html.Div(
                    className='four columns card',
                    children=[
                        html.Div(
                            className='row',
                            style={
                                'display': 'flex',
                                'justifyContent': 'space-around',
                                'alignItems': 'center',
                            },
                            children=[
                                html.Div(
                                    id='temperature-display',
                                    className='card_container',
                                    **{
                                        'data-color': COLORS['foreground'],
                                        'data-unit': UNITS['temperature'],
                                        # 'data-radius': 50
                                    },
                                ),
                                html.H3('Temperature', className='card_container'),
                            ]
                        )
                    ]
                ),
                html.Div(
                    className='four columns card',
                    children=[
                        html.Div(
                            className='row',
                            style={
                                'display': 'flex',
                                'justifyContent': 'space-around',
                                'alignItems': 'center',
                            },
                            children=[
                                html.Div(
                                    id='humidity-display',
                                    className='card_container',
                                    **{
                                        'data-color': COLORS['colorway'][0],
                                        'data-unit': UNITS['humidity'],
                                        # 'data-radius': 50
                                    },
                                ),
                                html.H3('Humidity', className='card_container',)
                            ]
                        )
                    ]
                ),
                html.Div(
                    className='four columns card',
                    children=[
                        html.Div(
                            className='row',
                            style={
                                'display': 'flex',
                                'justifyContent': 'space-around',
                                'alignItems': 'center',
                            },
                            children=[
                                html.Div(
                                    id='pressure-display',
                                    className='card_container',
                                    **{
                                        'data-color': COLORS['colorway'][1],
                                        'data-unit': UNITS['pressure'],
                                        # 'data-radius': 50
                                    },
                                ),
                                html.H3('Pressure', className='card_container',)
                            ]
                        )
                    ]
                ),
            ],
        ),

        html.Div(
            className='row card_row',
            children=[
                html.Div(
                    className='six columns',
                    children=[
                        html.Div(
                            className='row card',
                            children=[
                                html.H6(
                                    "Last 24 hours",
                                    className="data__overview__day__title title__center",
                                    style={'marginBottom': 0, 'marginTop': 0},
                                ),
                                html.Div(
                                    className="six column graph_in_column",
                                    style={'padding': '0px 10px 10px 10px'},
                                    children=[
                                        dcc.Graph(
                                            id="day-data-graph",
                                            style={'height': '25vh'},
                                            config={
                                                'staticPlot': False,
                                                'displayModeBar': False,
                                            },
                                            className="graph",
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                html.Div(
                    className='six columns',
                    children=[
                        html.Div(
                            className='row',
                            children=[
                                html.Div(
                                    className='six columns card',
                                    children=[
                                        html.Div(
                                            className='row',
                                            style={
                                                'display': 'flex',
                                                'justifyContent': 'space-around',
                                                'alignItems': 'center',
                                            },
                                            children=[
                                                html.Img(
                                                    src='assets/altitude_icon.svg.png',
                                                    style={
                                                        'height': '50px',
                                                        'width': '50px'
                                                    },
                                                ),
                                                html.H4(
                                                    id='altitude-display',
                                                ),
                                            ]
                                        )
                                    ],
                                ),
                                html.Div(
                                    className='six columns card',
                                    children=[
                                        html.Div(
                                            className='row',
                                            style={
                                                'display': 'flex',
                                                'justifyContent': 'space-around',
                                                'alignItems': 'center',
                                            },
                                            children=[
                                                html.Img(
                                                    src=app.get_asset_url('brightness_icon.svg.png'),
                                                    style={
                                                        'height': '50px',
                                                        'width': '50px'
                                                    },
                                                ),
                                                html.H4(
                                                    id='brightness-display',
                                                ),
                                            ]
                                        )
                                    ],
                                ),
                            ],
                        ),
                        # calendar is supposed to go here
                    ],
                )
            ],
        ),
    ]
)

app.clientside_callback(
    ClientsideFunction(
        namespace='clientside_2',
        function_name='make_radial_indicator'
    ),
    Output('temperature-display', 'children'),
    [Input('temperature-display', 'id'),
     Input('temperature_store', 'data')]
)


app.clientside_callback(
    ClientsideFunction(
        namespace='clientside_2',
        function_name='make_radial_indicator'
    ),
    Output('humidity-display', 'children'),
    [Input('humidity-display', 'id'),
     Input('humidity_store', 'data')]
)


app.clientside_callback(
    ClientsideFunction(
        namespace='clientside_2',
        function_name='make_radial_indicator'
    ),
    Output('pressure-display', 'children'),
    [Input('pressure-display', 'id'),
     Input('pressure_store', 'data')]
)


@app.callback(
    Output('altitude-display', 'children'),
    [Input('last_entry', 'data')]
)
def get_altitude(data):
    if data:
        logger.debug(f"Updating altitude display ({round(data['altitude'], 2)} m).")
        return f"{round(data['altitude'], 2)} m"
    return ''


@app.callback(
    Output('brightness-display', 'children'),
    [Input('last_entry', 'data')]
)
def get_brightness(data):
    if data:
        logger.debug(f"Updating brightness display ({round(data['brightness'], 2)} lx).")
        return f"{round(data['brightness'], 2)} lx"
    return ''


@app.callback(
    Output('last_entry', 'data'),
    [Input('data-overview-update', 'n_intervals')],
    [State('error-store', 'data')]
)
def update_last_value(n, errors):
    if errors['room-data']:
        logger.warning("RoomData table does not exist. Cant fetch latest data.")
        last = None
    elif not sql.is_data_in_roomdata_table():
        logger.warning("RoomData table has no entries. Cant fetch latest data.")
        last = None
    else:
        last = sql.get_latest_roomdata()
        logger.debug(f"Updating last values store ({last}).")
    return last


@app.callback(
    Output('temperature_store', 'data'),
    [Input('last_entry', 'data')],
    [State('temperature_store', 'data')]
)
def update_temperature_store(latest_data, old_data):
    if latest_data:
        last = latest_data['temperature']
        logger.debug(f"Updating temperature store ({round(last, 2)}).")
        if (old_data and old_data['display'] == 0) or not old_data:
            old_data = {
                'display': 1,
                'new': last,
                'old': 0,
                'min': floor(sql.get_min_temperature_roomdata()),
                'max': ceil(sql.get_max_temperature_roomdata()),
            }
        else:
            if last > old_data['max']:
                old_data['max'] = last
            elif last < old_data['min']:
                old_data['min'] = last

            old_data['old'] = old_data['new']
            old_data['new'] = last
    else:
        old_data = {
            'new': 0,
            'old': 0,
            'min': 0,
            'max': 0,
            'display': 0
        }
    return old_data


@app.callback(
    Output('pressure_store', 'data'),
    [Input('last_entry', 'data')],
    [State('pressure_store', 'data')]
)
def update_pressure_store(latest_data, old_data):
    if latest_data:
        last = latest_data['pressure']
        logger.debug(f"Updating pressure store ({round(last, 2)}).")
        if (old_data and old_data['display'] == 0) or not old_data:
            old_data = {
                'display': 1,
                'new': last,
                'old': 0,
                'min': floor(sql.get_min_pressure_roomdata()),
                'max': ceil(sql.get_max_pressure_roomdata()),
            }
        else:
            if last > old_data['max']:
                old_data['max'] = last
            elif last < old_data['min']:
                old_data['min'] = last

            old_data['old'] = old_data['new']
            old_data['new'] = last
    else:
        old_data = {
            'new': 0,
            'old': 0,
            'min': 0,
            'max': 0,
            'display': 0
        }
    return old_data


@app.callback(
    Output('humidity_store', 'data'),
    [Input('last_entry', 'data')],
    [State('humidity_store', 'data')]
)
def update_humidity_store(latest_data, old_data):
    if latest_data:
        last = latest_data['humidity']
        logger.debug(f"Updating humidity store ({round(last, 2)}).")
        if (old_data and old_data['display'] == 0) or not old_data:
            old_data = {
                'display': 1,
                'new': last,
                'old': 0,
                'min': floor(sql.get_min_humidity_roomdata()),
                'max': ceil(sql.get_max_humidity_roomdata()),
            }
        else:
            if last > old_data['max']:
                old_data['max'] = last
            elif last < old_data['min']:
                old_data['min'] = last

            old_data['old'] = old_data['new']
            old_data['new'] = last
    else:
        old_data = {
            'new': '?',
            'old': 0,
            'min': 0,
            'max': 0,
            'display': 0
        }
    return old_data


@app.callback(
    Output('day-data-graph', 'figure'),
    [Input('data-overview-update', 'n_intervals')],
    [State('error-store', 'data')]
)
def update_day_graph(interval, errors):
    fig = go.Figure()

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
            'fixedrange': True,
            'showline': True, 'linewidth': 1,
            'linecolor': COLORS['border-medium'],
            'showgrid': True, 'gridwidth': 1,
            'zeroline': True, 'zerolinewidth': 1,
            'zerolinecolor': COLORS['border-medium'],
        },
        'yaxis': {
            'gridcolor': COLORS['dark-2'],
            'fixedrange': True,
            'showline': True, 'linewidth': 1,
            'linecolor': COLORS['border-medium'],
            'showgrid': True, 'gridwidth': 1,
            'zeroline': True, 'zerolinewidth': 1,
            'zerolinecolor': COLORS['border-medium'],
        }
    })

    if errors['room-data']:
        logger.warning("RoomData table does not exist. Can't get last 24 hours data.")
        return fig
    elif not sql.is_data_in_roomdata_table():
        logger.warning("RoomData table has no entries. Can't get last 24 hours data.")
        return fig
    else:
        logger.debug("Updating last 24 hours temperature graph.")

    now = datetime.now()
    start = now - relativedelta(days=1)

    data_query = sql.get_last_24_hrs(start, now)
    if data_query.count():
        day_data = pd.DataFrame([{'date': value[0], 'temperature': value[1]} for value in data_query])

        if day_data['temperature'].count() > 10:
            # Design of Buterworth filter
            filter_order = 2    # Filter order
            cutoff_freq = 0.2   # Cutoff frequency
            B, A = signal.butter(filter_order, cutoff_freq, output='ba')

            # Apply filter
            tempf = signal.filtfilt(B, A, day_data['temperature'])
        else:
            tempf = day_data['temperature']

        fig.add_trace(go.Scatter(
            x=day_data['date'],
            y=tempf,
            mode='lines',
            name='temperature',
            line={'color': COLORS['foreground']},
            hovertemplate="%{x|%d.%m.%Y} : %{y:.2f}°C",
        ))
    return fig
