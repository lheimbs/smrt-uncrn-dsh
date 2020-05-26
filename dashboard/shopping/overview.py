#!/usr/bin/env python3

import logging
from datetime import datetime
from calendar import month_name
from dateutil.relativedelta import relativedelta

import numpy as np
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
from plotly.subplots import make_subplots

from .. import graph_helper
from ..app import app, COLORS
from .sql import (
    get_shopping_expenses_by_date,
    get_unique_shopping_days,
    get_unique_shopping_shops,
    get_shopping_expenses_per_shop,
    get_all_lists
)

logger = logging.getLogger()

layout = html.Div(
    className='row',
    children=[
        html.Div(
            className='row',
            style={'height': '50vh'},
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
                    className='six columns',
                    children=[
                        html.Div(
                            className='row',
                            children=[
                                dcc.Loading(
                                    id="loading-shopping-category-month-graph",
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
                            ],
                        ),
                        html.Div(
                            className='row',
                            children=[
                                dcc.Loading(
                                    id="loading-shopping-category-total-graph",
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
                            ],
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            className='row',
            style={'height': '40vh'},
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
    [Input("loading-shopping-overview-graph", 'loading_state')],
    [State('error-store', 'data')]
)
def get_shopping_monthly_overview(state, errors):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

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
            'l': 10, 'r': 10, 'b': 0, 't': 40, 'pad': 0,
        },
        'paper_bgcolor': COLORS['background'],
        'plot_bgcolor': COLORS['background'],
        'title': {
            'text': "Monthly expenses Overview",
        },
        'xaxis': {
            'fixedrange': True, 'rangemode': 'tozero',
            'showline': True, 'linewidth': 1, 'linecolor': COLORS['border-medium'],
            'showgrid': True, 'gridwidth': 1, 'gridcolor': COLORS['border-medium'],
            'zeroline': True, 'zerolinewidth': 1, 'zerolinecolor': COLORS['border-medium'],
        },
        'yaxis': {
            'side': 'right',
            'fixedrange': True, 'rangemode': 'tozero',
            'showline': True, 'linewidth': 1, 'linecolor': COLORS['border-medium'],
            'showgrid': True, 'gridwidth': 1, 'gridcolor': COLORS['border-medium'],
            'zeroline': True, 'zerolinewidth': 1, 'zerolinecolor': COLORS['border-medium'],
        },
        'yaxis2': {
            'side': 'left',
            'overlaying': 'y',
            'fixedrange': True, 'rangemode': 'tozero',
            'showline': True, 'linewidth': 1, 'linecolor': COLORS['border-medium'],
            'showgrid': True, 'gridwidth': 1, 'gridcolor': COLORS['border-medium'],
            'zeroline': True, 'zerolinewidth': 1, 'zerolinecolor': COLORS['border-medium'],
        },
    })

    if errors['list'] or errors['category'] or errors['shop'] or errors['item']:
        logger.warning("Neccessary Shopping tables do not exist in database!")
        return fig

    six_months_ago = datetime.now()-relativedelta(months=6)
    six_months_ago = datetime(six_months_ago.year, six_months_ago.month, 1)

    data = get_shopping_expenses_by_date(six_months_ago)
    if data.empty:
        logger.warning(f"No shopping entries found since {six_months_ago}.")
        return fig

    curr_month = data.date.dt.month.unique()[-1]
    unique_months = data.date.dt.month.unique()

    max_min = list(
        zip(
            *[
                (x.price.cumsum().max(), x.price.cumsum().min())
                for _, x in data[data.date.dt.month != curr_month].set_index('date').groupby(lambda x: x.month)
            ]
        )
    )

    y1_max, y1_min = max(max_min[0]), min(max_min[1])
    y2_min, y2_max = (
        data[data.date.dt.month == curr_month].price.min(),
        data[data.date.dt.month == curr_month].price.max(),
    )
    y1_range_min, y1_range_max, y1_dtick, y2_range_min, y2_range_max, y2_dtick = graph_helper.calculate_ticks(
        y1_min, y1_max, y2_min, y2_max
    )

    fig.update_layout({
        'yaxis': {
            'range': [y2_range_min, y2_range_max],
            'dtick': y2_dtick,
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

    for month in unique_months:
        months_data = pd.DataFrame({
            'Days': data[data.date.dt.month == month].date.dt.day,
            'price': data[data.date.dt.month == month].price.cumsum()
        })
        months_data.loc[-1] = 0
        months_data.index = months_data.index + 1
        months_data = months_data.sort_index()
        if months_data.Days.iloc[-1] != 31 and (month != unique_months[-1] or month != datetime.now().month):
            months_data = months_data.append(
                {'Days': 31, 'price': np.interp([31], months_data.Days, months_data.price)[0]},
                ignore_index=True
            )

        trace = go.Scatter(
            mode='lines',
            hovertemplate='%{x}.: %{y:.2f}€',
            x=months_data.Days,
            y=months_data.price,
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
                    hovertemplate="%{x}.: %{y:.2f}€",
                    x=data[data.date.dt.month == month].date.dt.day,
                    y=data[data.date.dt.month == month].price,
                    name=month_name[month],
                    marker={
                        'color': COLORS['foreground'],
                    },
                ),
                secondary_y=False,
            )
    return fig


@app.callback(
    Output('shopping-category-month-graph', 'figure'),
    [Input('loading-shopping-category-month-graph', 'loading_state')],
    [State('error-store', 'data')]
)
def get_shopping_expenses_type_overview(state, errors):
    fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'domain'}, {'type': 'domain'}]])

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
        'height': 250,
        'legend': {
            'orientation': 'v',
        },
        'margin': {
            'l': 10, 'r': 10, 'b': 40, 't': 40, 'pad': 0,
        },
        'paper_bgcolor': COLORS['background'],
        'plot_bgcolor': COLORS['background'],
        'title': {
            'text': "Shopping categories",
        },
        'xaxis': {
            'fixedrange': True,
            'showline': False,
            'showgrid': False,
            'zeroline': False,
        },
        'yaxis': {
            'fixedrange': True,
            'showline': False,
            'showgrid': False,
            'zeroline': False,
        },
    })

    if errors['list'] or errors['category'] or errors['shop'] or errors['item']:
        logger.warning("Neccessary Shopping tables do not exist in database!")
        return fig

    expenses = get_all_lists()
    expenses = pd.DataFrame(
        [(liste.date, liste.price, liste.shop.category.name) for liste in expenses.all()],
        columns=['date', 'price', 'category']
    )
    labels = expenses.category
    fig.add_trace(
        go.Pie(
            labels=labels,
            values=expenses.price,
            name='This months categories',
        ),
        1, 2,
    )

    this_month = datetime(datetime.now().year, datetime.now().month, 1)
    expenses.loc[expenses.date < this_month, "price"] = 0
    fig.add_trace(
        go.Pie(
            labels=labels,
            values=expenses.price,
            name='This months categories',
            textposition='inside'
        ),
        1, 1,
    )

    fig.update_traces(
        hovertemplate="%{label}: %{value:.2f}€ (%{percent})<extra></extra>",
        marker=dict(
            colors=[COLORS['foreground']]+COLORS['colorway'],
        )
    )
    return fig


@app.callback(
    Output('shopping-category-total-graph', 'figure'),
    [Input('loading-shopping-category-total-graph', 'loading_state')],
    [State('error-store', 'data')]
)
def get_shopping_category_total_overview(state, errors):
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
        'height': 250,
        'legend': {
            'orientation': 'v',
        },
        'margin': {
            'l': 10, 'r': 10, 'b': 40, 't': 40, 'pad': 0,
        },
        'paper_bgcolor': COLORS['background'],
        'plot_bgcolor': COLORS['background'],
        'title': {
            'text': "Total category Overview",
        },
        'xaxis': {
            'fixedrange': True,
            'showline': False,
            'showgrid': False,
            'zeroline': False,
        },
        'yaxis': {
            'fixedrange': True,
            'showline': False,
            'showgrid': False,
            'zeroline': False,
        },
    })

    if errors['list'] or errors['category'] or errors['shop'] or errors['item']:
        logger.warning("Neccessary Shopping tables do not exist in database!")
        return fig

    expenses = get_all_lists()
    expenses = pd.DataFrame(
        [(liste.price, liste.shop.category.name) for liste in expenses.all()],
        columns=['price', 'category']
    )
    fig.add_trace(go.Pie(labels=expenses.category, values=expenses.price))

    fig.update_traces(
        hoverinfo='label+percent',
        textinfo='value', textfont_size=20,
        marker=dict(
            colors=COLORS['colorway'],
            line=dict(color='#000000', width=2)
        )
    )
    return fig


@app.callback(
    Output('shopping-overview-graph', 'figure'),
    [Input("loading-shopping-overview-graph", 'loading_state')],
    [State('error-store', 'data')]
)
def get_shopping_total_overview(state, errors):
    fig = go.Figure()
    fig.update_layout({
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
    })

    if errors['list'] or errors['category'] or errors['shop'] or errors['item']:
        logger.warning("Neccessary Shopping tables do not exist in database!")
        return fig

    df_days = get_unique_shopping_days()
    shops = get_unique_shopping_shops()
    shops = shops.sort_values('name')

    for shop in shops.name:
        expense = get_shopping_expenses_per_shop(shop)
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

        fig.add_trace(bar)

    return fig
