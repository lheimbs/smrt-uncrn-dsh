from datetime import datetime
from math import floor

import scipy.signal as signal
import plotly.graph_objects as go
from flask import current_app
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots

from .import sql
from ..variables import COLORS


def init_callbacks(app):                    # noqa: C901
    @app.callback(
        [
            Output('data-history-overlay', 'style'),
            Output('data-hist-sidebar-content', 'style'),
        ],
        [
            Input('data-history-overlay', 'loading_state'),
            Input('data-history-show-hide-switch', 'on'),
        ],
    )
    def display_data_history_overlay(state, toggle_button):
        if not toggle_button:
            return {'width': '0'}, {'marginLeft': '0'}
        return {'width': '15vw'}, {'marginLeft': '15vw'}

    app.clientside_callback(
        '''
        window.onload = function getGraphWidth() {
            if(!document.getElementById("data-history-graph")) {
                width = 0;
            }
            else {
                var width = document.getElementById("data-history-graph").clientWidth;
            }
            return width;
        };
        ''',
        Output('data-history-graph-current-width', 'data'),
        [Input('data-history-graph', 'loading_state')]
    )

    @app.callback(
        Output('data-history-graph', 'figure'),
        [
            Input('data-history-date-picker', 'start_date'),
            Input('data-history-date-picker', 'end_date'),
            Input('data-history-values', 'value'),
            Input('data-history-graph-current-width', 'data')
        ]
    )
    def update_history_graph(start_date, end_date, chosen_values, current_width):
        n_chosen = len(chosen_values) if len(chosen_values) else 1
        fig = make_subplots(
            rows=n_chosen,
            cols=1,
        )
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
                'family': "Ubuntu",
                'color': COLORS['font-foreground'],
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
                'showline': True, 'linewidth': 1,
                'linecolor': COLORS['border-medium'],
                'showgrid': True, 'gridwidth': 1,
                'zeroline': True, 'zerolinewidth': 1,
                'zerolinecolor': COLORS['border-medium'],
            },
            'xaxis2': {
                'gridcolor': COLORS['dark-2'],
                'showline': True, 'linewidth': 1,
                'linecolor': COLORS['border-medium'],
                'showgrid': True, 'gridwidth': 1,
                'zeroline': True, 'zerolinewidth': 1,
                'zerolinecolor': COLORS['border-medium'],
            },
            'xaxis3': {
                'gridcolor': COLORS['dark-2'],
                'showline': True, 'linewidth': 1,
                'linecolor': COLORS['border-medium'],
                'showgrid': True, 'gridwidth': 1,
                'zeroline': True, 'zerolinewidth': 1,
                'zerolinecolor': COLORS['border-medium'],
            },
            'xaxis4': {
                'gridcolor': COLORS['dark-2'],
                'showline': True, 'linewidth': 1,
                'linecolor': COLORS['border-medium'],
                'showgrid': True, 'gridwidth': 1,
                'zeroline': True, 'zerolinewidth': 1,
                'zerolinecolor': COLORS['border-medium'],
            },
            'xaxis5': {
                'gridcolor': COLORS['dark-2'],
                'showline': True, 'linewidth': 1,
                'linecolor': COLORS['border-medium'],
                'showgrid': True, 'gridwidth': 1,
                'zeroline': True, 'zerolinewidth': 1,
                'zerolinecolor': COLORS['border-medium'],
            },
            'yaxis': {
                'gridcolor': COLORS['dark-2'],
                'showline': True, 'linewidth': 1,
                'linecolor': COLORS['border-medium'],
                'showgrid': True, 'gridwidth': 1,
                'zeroline': True, 'zerolinewidth': 1,
                'zerolinecolor': COLORS['border-medium'],
            },
            'yaxis2': {
                'gridcolor': COLORS['dark-2'],
                'showline': True, 'linewidth': 1,
                'linecolor': COLORS['border-medium'],
                'showgrid': True, 'gridwidth': 1,
                'zeroline': True, 'zerolinewidth': 1,
                'zerolinecolor': COLORS['border-medium'],
            },
            'yaxis3': {
                'gridcolor': COLORS['dark-2'],
                'showline': True, 'linewidth': 1,
                'linecolor': COLORS['border-medium'],
                'showgrid': True, 'gridwidth': 1,
                'zeroline': True, 'zerolinewidth': 1,
                'zerolinecolor': COLORS['border-medium'],
            },
            'yaxis4': {
                'gridcolor': COLORS['dark-2'],
                'showline': True, 'linewidth': 1,
                'linecolor': COLORS['border-medium'],
                'showgrid': True, 'gridwidth': 1,
                'zeroline': True, 'zerolinewidth': 1,
                'zerolinecolor': COLORS['border-medium'],
            },
            'yaxis5': {
                'gridcolor': COLORS['dark-2'],
                'showline': True, 'linewidth': 1,
                'linecolor': COLORS['border-medium'],
                'showgrid': True, 'gridwidth': 1,
                'zeroline': True, 'zerolinewidth': 1,
                'zerolinecolor': COLORS['border-medium'],
            }
        })
        if current_width:
            current_width = (current_width / 2) if current_width > 0 else 1
        else:
            current_width = 1

        if (start_date is None and end_date is None):
            return fig
        elif not sql.is_data_in_roomdata_table():
            current_app.logger.warning("RoomData table has no entries. Cant fetch latest data.")
            return fig

        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        data_query = sql.get_data_between(start_date, end_date)

        data_count = data_query.count()
        if not data_count:
            return fig

        nth_row = floor(data_count / current_width) if data_count > current_width else 1
        nth_row = 60 if nth_row > 60 else nth_row

        current_app.logger.debug(f"current_width: {current_width}, data_count {data_count}, nth {nth_row}")
        data = sql.get_data_dict(data_query, nth_row)
        # data = pd.DataFrame([room_data.to_dict() for room_data in data_query.filter(RoomData.id % nth_row == 0)])

        for i, value in enumerate(chosen_values):
            if data[value].count() > 10:
                # Design of Buterworth filter
                filter_order = 2    # Filter order
                cutoff_freq = 0.2   # Cutoff frequency
                B, A = signal.butter(filter_order, cutoff_freq, output='ba')

                # Apply filter
                tempf = signal.filtfilt(B, A, data[value])
            else:
                tempf = data[value]

            fig.add_trace(
                go.Scatter(
                    mode='lines',
                    name=value,
                    x=data['date'],
                    y=tempf,
                ),
                row=i + 1, col=1,
            )
        return fig
