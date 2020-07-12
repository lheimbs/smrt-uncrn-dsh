import dash_core_components as dcc
import dash_html_components as html

from ..variables import COLORS

layout = html.Div(
    className="dahboard-overview-container",
    children=[
        html.Div(
            className='values-select-container card',
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
            className='daterange-select-container card',
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
                    with_full_screen_portal=False,
                ),
            ],
        ),
        html.Div(
            id='data-hist-sidebar-content',
            className="overview-graph-container",
            children=[
                dcc.Store(id='data-history-graph-current-width'),
                dcc.Loading(id="loading-1", color=COLORS['foreground'], children=[
                    dcc.Graph(
                        # style={'height': '70%'},
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
