#!/usr/bin/env python3

from datetime import datetime
from calendar import month_name
from dateutil.relativedelta import relativedelta

import numpy as np
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots

import shopping.graph_helper
from app import app, COLORS

layout = html.Div(
    className='row',
    children=[
        html.Div(
            className='row',
            children=[
                html.Div(
                    className='six columns',
                    children=[
                        dcc.Loading(id="loading-shopping-montly-graph", color=COLORS['foreground'], children=[
                            dcc.Graph(
                                id="shopping-month-graph",
                                clear_on_unhover=True,
                                config={
                                    'staticPlot': False,
                                    'displayModeBar': False,
                                },
                                className="shopping__monthly_graph graph",
                            ),
                        ], type="default"),
                    ],
                ),
                html.Div(
                    className='three columns',
                    children=[
                        dcc.Loading(
                            id="loading-shopping-expenses-type-graph",
                            color=COLORS['foreground'],
                            children=[
                                dcc.Graph(
                                    id="shopping-expenses-type-graph",
                                    clear_on_unhover=True,
                                    config={
                                        'staticPlot': False,
                                        'displayModeBar': False,
                                        'displaylogo': False,
                                    },
                                    className="shopping__expenses__type_graph graph",
                                ),
                            ],
                            type="default"
                        ),
                    ],
                ),
                html.Div(
                    className='three columns',
                    children=[
                        dcc.Loading(
                            id="loading-shopping-nutrition-type-graph",
                            color=COLORS['foreground'],
                            children=[
                                dcc.Graph(
                                    id="shopping-nutrition-type-graph",
                                    clear_on_unhover=True,
                                    config={
                                        'staticPlot': False,
                                        'displayModeBar': False,
                                    },
                                    className="shopping__nutrition__type_graph graph",
                                ),
                            ],
                            type="default"
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            className='row',
            children=[
                dcc.Loading(id="loading-shopping-overview-graph", color=COLORS['foreground'], children=[
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
                ], type="default"),
            ],
        ),
    ],
)


@app.callback(
    Output('shopping-month-graph', 'figure'),
    [Input("loading-shopping-overview-graph", 'loading_state')]
)
def get_shopping_monthly_overview(state):
    six_months_ago = datetime.now()-relativedelta(months=6)
    six_months_ago = datetime(six_months_ago.year, six_months_ago.month, 1)

    data = sql_data.get_shopping_expenses_by_date(six_months_ago)
    curr_month = data.Date.dt.month.unique()[-1]
    unique_months = data.Date.dt.month.unique()

    max_min = list(
        zip(
            *[
                (x.Payment.cumsum().max(), x.Payment.cumsum().min())
                for _, x in data[data.Date.dt.month != curr_month].set_index('Date').groupby(lambda x: x.month)
            ]
        )
    )

    y1_max, y1_min = max(max_min[0]), min(max_min[1])
    y2_min, y2_max = (
        data[data.Date.dt.month == curr_month].Payment.min(),
        data[data.Date.dt.month == curr_month].Payment.max(),
    )
    y1_range_min, y1_range_max, y1_dtick, y2_range_min, y2_range_max, y2_dtick = shopping.graph_helper.calculate_ticks(
        y1_min, y1_max, y2_min, y2_max
    )

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    for month in unique_months:
        months_data = pd.DataFrame({
            'Days': data[data.Date.dt.month == month].Date.dt.day,
            'Payment': data[data.Date.dt.month == month].Payment.cumsum()
        })
        months_data.loc[-1] = 0
        months_data.index = months_data.index + 1
        months_data = months_data.sort_index()
        if months_data.Days.iloc[-1] != 31 and (month != unique_months[-1] or month != datetime.now().month):
            months_data = months_data.append(
                {'Days': 31, 'Payment': np.interp([31], months_data.Days, months_data.Payment)[0]},
                ignore_index=True
            )

        trace = go.Scatter(
            mode='lines',
            hovertemplate='%{y:.2f}€',
            x=months_data.Days,
            y=months_data.Payment,
            name=month_name[month],
            yaxis='y2',
        )

        if month == unique_months[-1]:
            trace.line = {'color': COLORS['foreground']}

        fig.add_trace(
            trace,
            secondary_y=True,
        )
        if month == unique_months[-1]:
            fig.add_trace(
                go.Bar(
                    opacity=0.5,
                    hovertemplate='%{y:.2f}€',
                    x=data[data.Date.dt.month == month].Date.dt.day,
                    y=data[data.Date.dt.month == month].Payment,
                    name=month_name[month],
                    marker={
                        'color': COLORS['foreground'],
                    },
                ),
                secondary_y=False,
            )

    fig.update_layout({
        'autosize': True,
        'barmode': 'overlay',
        'coloraxis': {
            'colorbar': {
                'outlinewidth': 0,
                'bordercolor': COLORS['background'],
                'bgcolor': COLORS['background'],
            },
        },
        'colorway': COLORS['colorway'],
        'dragmode': False,
        'font': {
            'color': COLORS['foreground'],
        },
        'legend': {
            'orientation': 'h',
        },
        'margin': {
            'l': 10, 'r': 10, 't': 10, 'b': 10, 'pad': 0,
        },
        'paper_bgcolor': COLORS['background'],
        'plot_bgcolor': COLORS['background'],
        'xaxis': {
            'fixedrange': True, 'rangemode': 'tozero',
            'showline': True, 'linewidth': 1, 'linecolor': COLORS['border-medium'],
            'showgrid': True, 'gridwidth': 1, 'gridcolor': COLORS['border-medium'],
            'zeroline': True, 'zerolinewidth': 1, 'zerolinecolor': COLORS['border-medium'],
        },
        'yaxis': {
            'side': 'right',
            'range': [y2_range_min, y2_range_max],
            'dtick': y2_dtick,
            'fixedrange': True, 'rangemode': 'tozero',
            'showline': True, 'linewidth': 1, 'linecolor': COLORS['border-medium'],
            'showgrid': True, 'gridwidth': 1, 'gridcolor': COLORS['border-medium'],
            'zeroline': True, 'zerolinewidth': 1, 'zerolinecolor': COLORS['border-medium'],
        },
        'yaxis2': {
            'side': 'left',
            'range': [y1_range_min, y1_range_max],
            'dtick': y1_dtick,
            'overlaying': 'y',
            'fixedrange': True, 'rangemode': 'tozero',
            'showline': True, 'linewidth': 1, 'linecolor': COLORS['border-medium'],
            'showgrid': True, 'gridwidth': 1, 'gridcolor': COLORS['border-medium'],
            'zeroline': True, 'zerolinewidth': 1, 'zerolinecolor': COLORS['border-medium'],
        },
    })
    return fig


@app.callback(
    Output('shopping-expenses-type-graph', 'figure'),
    [Input('loading-shopping-expenses-type-graph', 'loading_state')]
)
def get_shopping_expenses_type_overview(state):
    # this_month = datetime(datetime.now().year, datetime.now().month, 1)
    # expenses_this_month = sql_data.get_shopping_expenses_by_date(this_month)
    fig = go.Figure()

    fig.update_layout({
        'autosize': True,
        'barmode': 'overlay',
        'coloraxis': {
            'colorbar': {
                'outlinewidth': 0,
                'bordercolor': COLORS['background'],
                'bgcolor': COLORS['background'],
            },
        },
        'colorway': COLORS['colorway'],
        'dragmode': False,
        'font': {
            'color': COLORS['foreground'],
        },
        'legend': {
            'orientation': 'h',
        },
        'margin': {
            'l': 10, 'r': 10, 't': 10, 'b': 10, 'pad': 0,
        },
        'paper_bgcolor': COLORS['background'],
        'plot_bgcolor': COLORS['background'],
        'xaxis': {
            'fixedrange': True, 'rangemode': 'tozero',
            'showline': True, 'linewidth': 1, 'linecolor': COLORS['border-medium'],
            'showgrid': True, 'gridwidth': 1, 'gridcolor': COLORS['border-medium'],
            'zeroline': True, 'zerolinewidth': 1, 'zerolinecolor': COLORS['border-medium'],
        },
        'yaxis': {
            'fixedrange': True, 'rangemode': 'tozero',
            'showline': True, 'linewidth': 1, 'linecolor': COLORS['border-medium'],
            'showgrid': True, 'gridwidth': 1, 'gridcolor': COLORS['border-medium'],
            'zeroline': True, 'zerolinewidth': 1, 'zerolinecolor': COLORS['border-medium'],
        },
    })
    return fig


@app.callback(
    Output('shopping-nutrition-type-graph', 'figure'),
    [Input('loading-shopping-nutrition-type-graph', 'loading_state')]
)
def get_shopping_nutrition_type_graph(state):
    fig = go.Figure()

    fig.update_layout({
        'autosize': True,
        'barmode': 'overlay',
        'coloraxis': {
            'colorbar': {
                'outlinewidth': 0,
                'bordercolor': COLORS['background'],
                'bgcolor': COLORS['background'],
            },
        },
        'colorway': COLORS['colorway'],
        'dragmode': False,
        'font': {
            'color': COLORS['foreground'],
        },
        'legend': {
            'orientation': 'h',
        },
        'margin': {
            'l': 10, 'r': 10, 't': 10, 'b': 10, 'pad': 0,
        },
        'paper_bgcolor': COLORS['background'],
        'plot_bgcolor': COLORS['background'],
        'xaxis': {
            'fixedrange': True, 'rangemode': 'tozero',
            'showline': True, 'linewidth': 1, 'linecolor': COLORS['border-medium'],
            'showgrid': True, 'gridwidth': 1, 'gridcolor': COLORS['border-medium'],
            'zeroline': True, 'zerolinewidth': 1, 'zerolinecolor': COLORS['border-medium'],
        },
        'yaxis': {
            'fixedrange': True, 'rangemode': 'tozero',
            'showline': True, 'linewidth': 1, 'linecolor': COLORS['border-medium'],
            'showgrid': True, 'gridwidth': 1, 'gridcolor': COLORS['border-medium'],
            'zeroline': True, 'zerolinewidth': 1, 'zerolinecolor': COLORS['border-medium'],
        },
    })
    return fig


@app.callback(
    Output('shopping-overview-graph', 'figure'),
    [Input("loading-shopping-overview-graph", 'loading_state')]
)
def get_shopping_total_overview(state):
    df_days = sql_data.get_unique_shopping_days()
    shops = sql_data.get_unique_shopping_shops()
    shops = shops.sort_values('Shop')

    data = []
    for shop in shops.Shop:
        expense = sql_data.get_shopping_expenses_per_shop(shop)
        df_days = df_days.join(expense)
        bar = go.Bar(
            name=shop,
            x=df_days.index,
            y=df_days[shop],
            hovertemplate="%{x|%d.%m.%Y} : %{y:.2f}€",
            marker={
                'line': {
                    'width': 0,
                    'color': COLORS['background'],
                }
            }
        )

        if shop.lower() == 'rewe':
            bar.marker['color'] = COLORS['colorway'][0]
        elif shop.lower() == 'aldi':
            bar.marker['color'] = COLORS['colorway'][1]
        elif shop.lower() == 'amazon':
            bar.marker['color'] = COLORS['colorway'][2]
        elif shop.lower() == 'bike24':
            bar.marker['color'] = COLORS['foreground']

        data.append(bar)

    fig = go.Figure(
        data=data,
        layout={
            'autosize': True,
            'barmode': 'stack',
            'coloraxis': {
                'colorbar': {
                    'outlinewidth': 0,
                    'bordercolor': COLORS['background'],
                    'bgcolor': COLORS['background'],
                },
            },
            'colorway': COLORS['colorway'][3:],
            'font': {
                'color': COLORS['foreground'],
            },
            'legend': {
                'orientation': 'h',
            },
            'margin': {
                'l': 10, 'r': 10, 't': 10, 'b': 10, 'pad': 0,
            },
            'paper_bgcolor': COLORS['background'],
            'plot_bgcolor': COLORS['background'],
            'xaxis': {
                'type': 'date',
                'range': [datetime(datetime.now().year-1, datetime.now().month, datetime.now().day), datetime.now()],
                'showline': True, 'linewidth': 1, 'linecolor': COLORS['border-medium'],
                'showgrid': True, 'gridwidth': 1, 'gridcolor': COLORS['border-medium'],
                'zeroline': True, 'zerolinewidth': 1, 'zerolinecolor': COLORS['border-medium'],
            },
            'yaxis': {
                'showline': True, 'linewidth': 1, 'linecolor': COLORS['border-medium'],
                'showgrid': True, 'gridwidth': 1, 'gridcolor': COLORS['border-medium'],
                'zeroline': True, 'zerolinewidth': 1, 'zerolinecolor': COLORS['border-medium'],
            },
        }
    )
    return fig
