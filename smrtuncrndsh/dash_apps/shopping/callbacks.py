from datetime import datetime
from dateutil.relativedelta import relativedelta
from calendar import month_name

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from flask import current_app
from plotly.subplots import make_subplots
from dash.dependencies import Input, Output

from .import sql, graph_helper
from ..variables import COLORS


def init_callbacks(app):                    # noqa: C901
    @app.callback(
        Output('shopping-month-graph', 'figure'),
        [Input("loading-shopping-overview-graph", 'loading_state')]
    )
    def get_shopping_monthly_overview(state):
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
        if not sql.is_data_in_shopping_tables():
            current_app.logger.warning("Neccessary Shopping tables do not exist in database!")
            return fig

        six_months_ago = datetime.now() - relativedelta(months=6)
        six_months_ago = datetime(six_months_ago.year, six_months_ago.month, 1)

        data = sql.get_shopping_expenses_by_date(six_months_ago)
        if data.empty:
            current_app.logger.warning(f"No shopping entries found since {six_months_ago}.")
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

        if max_min:
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
        [Input('loading-shopping-category-month-graph', 'loading_state')]
    )
    def get_shopping_expenses_type_overview(state):
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

        if not sql.is_data_in_shopping_tables():
            current_app.logger.warning("Neccessary Shopping tables do not exist in database!")
            return fig

        expenses = sql.get_all_lists()

        if not expenses.count():
            return fig

        expenses = pd.DataFrame(
            [(
                liste.date,
                liste.price,
                liste.shop.category.name if liste.shop.category else None,
            ) for liste in expenses],
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
                colors=[COLORS['foreground']] + COLORS['colorway'],
            )
        )
        return fig

    @app.callback(
        Output('shopping-category-total-graph', 'figure'),
        [Input('loading-shopping-category-total-graph', 'loading_state')]
    )
    def get_shopping_category_total_overview(state):
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

        if not sql.is_data_in_shopping_tables():
            current_app.logger.warning("Neccessary Shopping tables do not exist in database!")
            return fig

        expenses = sql.get_all_lists()
        if not expenses.count():
            return fig

        expenses = pd.DataFrame(
            [(liste.price, liste.shop.category.name if liste.shop.category else None) for liste in expenses],
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
        [Input("loading-shopping-overview-graph", 'loading_state')]
    )
    def get_shopping_total_overview(state):
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
                'range': [datetime(datetime.now().year - 1, datetime.now().month, datetime.now().day), datetime.now()],
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

        if not sql.is_data_in_shopping_tables():
            current_app.logger.warning("Neccessary Shopping tables do not exist in database!")
            return fig

        df_days = sql.get_unique_shopping_days()
        shops = sql.get_unique_shopping_shops()
        shops = shops.sort_values('name')

        for shop in shops.name:
            expense = sql.get_shopping_expenses_per_shop(shop)
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
