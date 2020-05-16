#!/usr/bin/env python3

import logging
from datetime import datetime

import scipy.signal as signal
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app, COLORS

logger = logging.getLogger()

EMPTY_GRAPH = {
    'data': [{'x': [], 'y': [], }, ],
    'layout':
    {
        'backgroundColor': COLORS['background'],
        'paper_bgcolor': COLORS['background'],
        'plot_bgcolor': COLORS['background'],
        'font': {
            'color': COLORS['foreground-dark']
        },
        'margin': {'l': 30, 'b': 30, 'r': 10, 't': 30},
        # 'width': '100%',
        'height': '250',
    }
}

layout = html.Div(
    className="row",
    children=[
        html.Div(
            children=[
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
                    with_full_screen_portal=True,
                ),
            ],
            className="two columns",
        ),
        html.Div(
            children=[
                dcc.Loading(id="loading-1", color=COLORS['foreground'], children=[
                    dcc.Graph(
                        id="data-history-graph",
                        figure=EMPTY_GRAPH,
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
            className="ten columns",
        )
    ],
)


@app.callback(
    Output('data-history-graph', 'figure'),
    [Input('data-history-date-picker', 'start_date'),
     Input('data-history-date-picker', 'end_date')])
def update_history_graph(start_date, end_date):
    if start_date is not None and end_date is not None:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        data = sql_data.get_temp_history(start_date, end_date)

        if data.empty:
            return EMPTY_GRAPH

        # Design of Buterworth filter
        filter_order = 2    # Filter order
        cutoff_freq = 0.2   # Cutoff frequency
        B, A = signal.butter(filter_order, cutoff_freq, output='ba')

        # Apply filter
        tempf = signal.filtfilt(B, A, data['temperature'], axis=0)

        return {
            'data': [
                {
                    'x': data['datetime'],
                    'y': tempf,
                    'type': 'scatter',
                    'name': 'Data',
                    'mode': 'lines'
                },
            ],
            'layout':
            {
                'backgroundColor': COLORS['background'],
                'paper_bgcolor': COLORS['background'],
                'plot_bgcolor': COLORS['background'],
                'font': {
                    'color': COLORS['foreground-dark']
                },
                'margin': {'l': 30, 'b': 30, 'r': 10, 't': 10},
                # 'width': '100%',
                'height': '500',
            }
        }
    else:
        return EMPTY_GRAPH
