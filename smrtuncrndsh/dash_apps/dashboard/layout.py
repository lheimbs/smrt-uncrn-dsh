import dash_core_components as dcc
import dash_html_components as html
from flask import url_for

from ..variables import GRAPH_INTERVAL, COLORS, UNITS


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
                            className="dash-graph",
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
                html.Div(
                    className="computer-status-container device-state card tooltip",
                    id="computer-status-container",
                    children=[
                        html.H6("computer", className="material-icons"),
                        html.H6(
                            id='computer-status',
                        ),
                        html.Span(
                            "Computer",
                            className="tooltiptext",
                        ),
                    ]
                ),
                html.Div(
                    className="voice_assistant-status-container device-state card tooltip",
                    id="voice_assistant-status-container",
                    children=[
                        html.H6("mic", className="material-icons"),
                        html.H6(
                            id='voice_assistant-status',
                        ),
                        html.Span(
                            "Terminator",
                            className="tooltiptext",
                        ),
                    ]
                ),
                html.Div(
                    className="esp_bme_rf-status-container device-state card tooltip",
                    id="esp_bme_rf-status-container",
                    children=[
                        html.H6("fireplace", className="material-icons"),
                        html.H6(
                            id='esp_bme_rf-status',
                        ),
                        html.Span(
                            "Room Sensors",
                            className="tooltiptext",
                        ),
                    ]
                ),
                html.Div(
                    className="smrt-uncrn-cllctr-status-container device-state card tooltip",
                    id="smrt-uncrn-cllctr-status-container",
                    children=[
                        html.H6("developer_board", className="material-icons"),
                        html.H6(
                            id='smrt-uncrn-cllctr-status',
                        ),
                        html.Span(
                            "Smrt-Uncrn-Cllctr",
                            className="tooltiptext",
                        ),
                    ]
                ),
                html.Div(
                    className="tablet-status-container device-state card tooltip",
                    id="tablet-status-container",
                    children=[
                        html.H6("tablet_android", className="material-icons"),
                        html.H6(id='tablet-status'),
                        html.H6(id='tablet-level'),
                        html.Span(
                            "tablet",
                            className="tooltiptext",
                        ),
                    ]
                ),
            ],
        ),
    ]
)
