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
                            id="loading-shopping-month-graph-id",
                            className="loading-shopping-month-graph",
                            color=COLORS['foreground'],
                            type="default",
                            children=[
                                dcc.Graph(
                                    id="shopping-month-graph",
                                    className="dash-graph",
                                    clear_on_unhover=True,
                                    config={
                                        'staticPlot': False,
                                        'displayModeBar': False,
                                    },
                                ),
                            ],
                        ),
                    ]
                ),
                html.Div(
                    className='shopping-category-month-graph-container',
                    children=[
                        dcc.Loading(
                            id="loading-shopping-category-month-graph-id",
                            className="loading-shopping-category-month-graph",
                            color=COLORS['foreground'],
                            children=[
                                dcc.Graph(
                                    id="shopping-category-month-graph",
                                    className="dash-graph",
                                    clear_on_unhover=True,
                                    config={
                                        'staticPlot': False,
                                        'displayModeBar': False,
                                        'displaylogo': False,
                                        'responsive': True,
                                    },
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
                            id="loading-shopping-category-total-graph-id",
                            className="loading-shopping-category-total-graph",
                            color=COLORS['foreground'],
                            children=[
                                dcc.Graph(
                                    id="shopping-category-total-graph",
                                    className="dash-graph",
                                    clear_on_unhover=True,
                                    config={
                                        'staticPlot': False,
                                        'displayModeBar': False,
                                        'displaylogo': False,
                                        'responsive': True,
                                    },
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
                            id="loading-shopping-overview-graph-id",
                            className="loading-shopping-overview-graph",
                            color=COLORS['foreground'],
                            type="default",
                            children=[
                                dcc.Graph(
                                    id="shopping-overview-graph",
                                    className="dash-graph",
                                    clear_on_unhover=True,
                                    config={
                                        'staticPlot': False,
                                        'displaylogo': False,
                                        'modeBarButtonsToRemove': [
                                            'select2d', 'lasso2d', 'autoScale2d',   # 2D
                                            'hoverClosest3d',   # 3D
                                            'hoverClosestCartesian', 'hoverCompareCartesian',   # Cartesian
                                            'zoomInGeo', 'zoomOutGeo', 'resetGeo', 'hoverClosestGeo',   # Geo
                                            'hoverClosestGl2d', 'hoverClosestPie', 'toggleHover',  # other
                                            'toImage', 'toggleSpikelines', 'resetViewMapbox', 'resetViews',  # other
                                        ],
                                    },
                                ),
                            ],
                        ),
                    ]
                ),
            ],
        ),
    ],
)
