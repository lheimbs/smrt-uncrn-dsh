import os

import dash_core_components as dcc
import dash_html_components as html
from flask import url_for

GRAPH_INTERVAL = os.environ.get("GRAPH_INTERVAL", 60000)
COLORS = {
    'foreground': '#7FDBFF',  # 4491ed',
    'foreground-dark': '#123456',
    'background': '#111111',
    'background-medium': '#252525',
    'background-sub-medium': '#1c1c1c',
    'border-light': '#d6d6d6',
    'border-medium': '#333333',
    'border-dark': '#0f0f0f',
    'dark-1': '#222222',
    'dark-2': '#333333',
    'red': 'red',
    'green': 'green',
    'error': '#960c0c',
    'success': '#17960c',
    'warning': '#f7b731',
    'colorway': [
        '#fc5c65',
        '#26de81',
        '#fd9644',
        '#2bcbba',
        '#a55eea',
        '#bff739',
        '#45aaf2',
        '#fed330',
        '#4b7bec',
        '#778ca3',
        '#eb3b5a',
        '#2d98da',
        '#fa8231',
        '#3867d6',
        '#f7b731',
        '#8854d0',
        '#20bf6b',
        '#a5b1c2',
        '#0fb9b1',
        '#4b6584',
    ]
}
UNITS = {
    'temperature': '°C',
    'pressure': 'hPa',
    'humidity': '%',
    'altitude': 'm',
    'brightness': 'lx',
}


layout = html.Div(
    className='dashboard-container',
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
            className='dashboard-content',
            children=[
                html.Div(
                    className="temperature-current-container card",
                    children=[
                        html.H3('Temperature', className='card_container'),
                        html.Div(
                            id='temperature-display',
                            className='card_container',
                            **{
                                'data-color': COLORS['foreground'],
                                'data-unit': UNITS['temperature'],
                                # 'data-radius': 50
                            },
                        ),
                    ]
                ),
                html.Div(
                    className="humidity-current-container card",
                    children=[
                        html.H3('Humidity', className='card_container'),
                        html.Div(
                            id='humidity-display',
                            className='card_container',
                            **{
                                'data-color': COLORS['colorway'][0],
                                'data-unit': UNITS['humidity'],
                                # 'data-radius': 50
                            },
                        ),
                    ]
                ),
                html.Div(
                    className="pressure-current-container card",
                    children=[
                        html.H3('Pressure', className='card_container'),
                        html.Div(
                            id='pressure-display',
                            className='card_container',
                            **{
                                'data-color': COLORS['colorway'][1],
                                'data-unit': UNITS['pressure'],
                                # 'data-radius': 50
                            },
                        ),
                    ]
                ),
                html.Div(
                    className="day-hrs-container card",
                    children=[
                        html.H6(
                            "Last 24 hours",
                            className="data__overview__day__title title__center",
                            style={'marginBottom': 0, 'marginTop': 0},
                        ),
                        dcc.Graph(
                            id="day-data-graph",
                            # style={'height': '25vh'},
                            config={
                                'staticPlot': False,
                                'displayModeBar': False,
                            },
                            className="graph",
                        ),
                    ]
                ),
                html.Div(
                    className="altitide-current-container card",
                    children=[
                        html.Img(
                            src=url_for('static', filename='img/altitude_icon.svg.png'),
                            style={
                                'height': '50px',
                                'width': '50px'
                            },
                        ),
                        html.H5(
                            id='altitude-display',
                        ),
                    ]
                ),
                html.Div(
                    className="brightness-current-container card",
                    children=[
                        html.Img(
                            src=url_for('static', filename='img/brightness_icon.svg.png'),
                            style={
                                'height': '50px',
                                'width': '50px'
                            },
                        ),
                        html.H5(
                            id='brightness-display',
                        ),
                    ]
                ),
            ],
        ),
    ]
)
