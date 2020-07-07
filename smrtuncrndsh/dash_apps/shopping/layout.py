import dash_core_components as dcc
import dash_html_components as html

from ..variables import COLORS

layout = html.Div(
    className='shopping-dashboard-container',
    children=[
        dcc.Store(
            id='shopping-products-store',
            storage_type='session',
        ),
        dcc.Store(
            id='shopping-shops-store',
            storage_type='session',
        ),
        html.Div(
            className='shopping-dashboard-content',
            children=[
                html.Div(
                    className='shopping-month-graph-container',
                    children=[
                        dcc.Loading(
                            className="loading-shopping-month-graph",
                            color=COLORS['foreground'],
                            type="default",
                            children=[
                                dcc.Graph(
                                    id="shopping-month-graph",
                                    clear_on_unhover=True,
                                    config={
                                        'staticPlot': False,
                                        'displayModeBar': False,
                                    },
                                    className="shopping__monthly_graph graph",
                                ),
                            ],
                        ),
                    ]
                ),
                html.Div(
                    className='shopping-category-month-graph-container',
                    children=[
                        dcc.Loading(
                            className="loading-shopping-category-month-graph",
                            color=COLORS['foreground'],
                            children=[
                                dcc.Graph(
                                    id="shopping-category-month-graph",
                                    clear_on_unhover=True,
                                    config={
                                        'staticPlot': False,
                                        'displayModeBar': False,
                                        'displaylogo': False,
                                        'responsive': True,
                                    },
                                    style={'height': '25vh'},
                                    className="shopping__category__type_graph graph",
                                ),
                            ],
                            type="default"
                        ),
                    ]
                ),
                html.Div(
                    className='shopping-category-total-graph-container',
                    children=[
                        dcc.Loading(
                            className="loading-shopping-category-total-graph",
                            color=COLORS['foreground'],
                            children=[
                                dcc.Graph(
                                    id="shopping-category-total-graph",
                                    clear_on_unhover=True,
                                    config={
                                        'staticPlot': False,
                                        'displayModeBar': False,
                                        'displaylogo': False,
                                    },
                                    className="",
                                ),
                            ],
                            type="default"
                        ),
                    ]
                ),
                html.Div(
                    className='shopping-overview-graph-container',
                    children=[
                        dcc.Loading(
                            className="loading-shopping-overview-graph",
                            color=COLORS['foreground'],
                            type="default",
                            children=[
                                dcc.Graph(
                                    id="shopping-overview-graph",
                                    clear_on_unhover=True,
                                    config={
                                        'staticPlot': False,
                                        'displaylogo': False,
                                        'modeBarButtonsToRemove': [
                                            'select2d', 'lasso2d', 'autoScale2d',   # 2D
                                            'hoverClosest3d',   # 3D
                                            'hoverClosestCartesian', 'hoverCompareCartesian',   # Cartesian
                                            'zoomInGeo', 'zoomOutGeo', 'resetGeo', 'hoverClosestGeo',   # Geo
                                            'hoverClosestGl2d', 'hoverClosestPie', 'toggleHover', 'resetViews',     # other
                                            'toImage', 'toggleSpikelines', 'resetViewMapbox',   # other
                                        ],
                                    },
                                    className="shopping__daily_graph graph",
                                ),
                            ],
                        ),
                    ]
                ),
            ],
        ),
    ],
)
