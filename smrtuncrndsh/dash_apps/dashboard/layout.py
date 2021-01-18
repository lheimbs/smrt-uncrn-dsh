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
        dcc.Store(id='weather'),

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
                    className="brightness-altitude-container",
                    children=[
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
                    ]
                ),
                html.Div(
                    className="computer-status-ctainer device-state card tooltip",
                    id="computer-status-container",
                    children=[
                        html.Div([
                            html.H6("computer", className="material-icons"),
                            html.H6(
                                id='computer-status',
                            ),
                            html.Span(
                                "Computer",
                                className="tooltiptext",
                            ),
                        ], className="status-details-container"),
                        html.P(id="computer-status-date", className="status-date")
                    ]
                ),
                html.Div(
                    className="voice_assistant-status-ctainer device-state card tooltip",
                    id="voice_assistant-status-container",
                    children=[
                        html.Div([
                            html.H6("mic", className="material-icons"),
                            html.H6(
                                id='voice_assistant-status',
                            ),
                            html.Span(
                                "Terminator",
                                className="tooltiptext",
                            ),
                        ], className="status-details-container"),
                        html.P(id="voice_assistant-status-date", className="status-date")
                    ]
                ),
                html.Div(
                    className="esp_bme_rf-status-ctainer device-state card tooltip",
                    id="esp_bme_rf-status-container",
                    children=[
                        html.Div([
                            html.H6("whatshot", className="material-icons"),
                            html.H6(
                                id='esp_bme_rf-status',
                            ),
                            html.Span(
                                "Room Sensors",
                                className="tooltiptext",
                            ),
                        ], className="status-details-container"),
                        html.P(id="esp_bme_rf-status-date", className="status-date")
                    ]
                ),
                html.Div(
                    className="smrt-uncrn-cllctr-status-ctainer device-state card tooltip",
                    id="smrt-uncrn-cllctr-status-container",
                    children=[
                        html.Div([
                            html.H6("developer_board", className="material-icons"),
                            html.H6(
                                id='smrt-uncrn-cllctr-status',
                            ),
                            html.Span(
                                "Smrt-Uncrn-Cllctr",
                                className="tooltiptext",
                            ),
                        ], className="status-details-container"),
                        html.P(id="smrt-uncrn-cllctr-status-date", className="status-date")
                    ]
                ),
                html.Div(
                    className="tablet-status-ctainer device-state card tooltip",
                    id="tablet-status-container",
                    children=[
                        html.Div([
                            html.H6("tablet_android", className="material-icons"),
                            html.H6(id='tablet-status'),
                            html.Div([
                                html.Span("battery_std", className="material-icons"),
                                html.H6(id='tablet-level'),
                            ], className="tablet-status-battery-cntnr"),
                            html.Span(
                                "Tablet",
                                className="tooltiptext",
                            ),
                        ], className="status-details-container"),
                        html.P(id="tablet-status-date", className="status-date")
                    ]
                ),
                html.Div(
                    className="weather-container card",
                    id="weather-container",
                    children=[
                        html.Div(
                            id="weather-current-container",
                            className="weather-current-container",
                            children=[
                                html.P(id="weather-current-date"),
                                html.H6(id="weather-current-location"),
                                html.Div([
                                    html.I(id="weather-current-icon", style={'margin-right': '5px'}),
                                    html.H6(id="weather-current-temp"),
                                ], className="weather-current-sub-container"),
                                html.P(id="weather-current-feel"),
                                html.Hr(),
                                html.Div([
                                    html.Div([
                                        html.Div([
                                            html.I(
                                                "navigation",
                                                className="material-icons",
                                                id="weather-current-wind-icon"
                                            ),
                                            html.P(id="weather-current-wind"),
                                        ], className="weather-current-sub-container"),
                                        html.P(id="weather-current-visibility"),
                                        html.P(id="weather-current-dew"),
                                    ], className="weather-current-details-side"),
                                    html.Div([
                                        html.P(id="weather-current-humidity"),
                                        html.P(id="weather-current-pressure"),
                                        html.P(id="weather-current-uv"),
                                    ], className="weather-current-details-side"),
                                ], className="weather-current-details"),
                            ]
                        ),
                        html.Div(
                            id="weather-hours-container",
                            className="weather-hours-container",
                            children=[
                                dcc.Graph(
                                    id="weather-hours-graph",
                                    style={'height': '15vh'},
                                    config={
                                        'staticPlot': False,
                                        'displayModeBar': False,
                                    },
                                    className="dash-graph",
                                ),
                            ]
                        ),
                        html.Div(
                            id="weather-days-container",
                            className="weather-days-container",
                        ),
                    ]
                ),
                html.Div(
                    id="shopping-info-container",
                    className="card",
                    children=[
                        html.Div(
                            className="shopping-info-text-container",
                            children=[
                                html.Div(
                                    className="shopping-info-row row-space-around",
                                    children=[
                                        html.H6("This month:", id="shopping-info-descriptor-1"),
                                        html.H6(id="shopping-info-current-month"),
                                        html.Span(id="shopping-info-current-month-weight", className="material-icons"),
                                    ]
                                ),
                                html.Div(
                                    className="shopping-info-row",
                                    children=[
                                        html.P(id="shopping-info-last-month"),
                                        html.P(id="shopping-info-last-6-months"),
                                    ]
                                )
                            ]
                        ),
                        html.Div(
                            id="shopping-info-graphs",
                            className="shopping-info-graphs-container",
                            children=[
                                dcc.Graph(
                                    id="shopping-info-category-month-graph",
                                    style={'height': '12vh'},
                                    config={
                                        'staticPlot': False,
                                        'displayModeBar': False,
                                    },
                                    className="dash-graph",
                                    # figure=fig,
                                ),
                            ]
                        )
                    ],
                ),
                # start corona data
                html.Div(
                    className="corona-data card",
                    children=[
                        html.Div(
                            className="corona-local-data",
                            children=[html.H6("Current COVID19 data:")]
                        ),
                        html.Div(
                            id="corona-local-data-1",
                            className="corona-local-data",
                            children=[
                                html.P(id="corona-local-data-1-error"),
                                html.Div(
                                    id="corona-local-data-1-header",
                                    className="corona-local-data-line",
                                    children=[
                                        html.H6(id="corona-local-data-1-header-county"),
                                        html.H5(id="corona-local-data-1-header-data"),
                                    ]
                                ),
                                html.Div(
                                    id="corona-local-data-1-footer",
                                    className="corona-local-data-line",
                                    children=[
                                        html.H6(id="corona-local-data-1-footer-state"),
                                        html.H5(id="corona-local-data-1-footer-data"),
                                    ]
                                )
                            ]
                        ),
                        html.Div(
                            id="corona-local-data-2",
                            className="corona-local-data",
                            children=[
                                html.P(id="corona-local-data-2-error"),
                                html.Div(
                                    id="corona-local-data-2-header",
                                    className="corona-local-data-line",
                                    children=[
                                        html.H6(id="corona-local-data-2-header-county"),
                                        html.H5(id="corona-local-data-2-header-data"),
                                    ]
                                ),
                                html.Div(
                                    id="corona-local-data-2-footer",
                                    className="corona-local-data-line",
                                    children=[
                                        html.H6(id="corona-local-data-2-footer-state"),
                                        html.H5(id="corona-local-data-2-footer-data"),
                                    ]
                                )
                            ]
                        ),
                        dcc.Graph(
                            id="corona-ger-data-graph",
                            style={'height': '10vh', 'width': '300px'},
                            config={
                                'staticPlot': False,
                                'displayModeBar': False,
                            },
                            className="dash-graph",
                        ),
                    ]
                ),
                # end corona data (for easier removing - hopefully soon)
            ],
        ),
    ]
)
