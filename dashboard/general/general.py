#!/usr/bin/env python3

import os
import logging

import dash_daq as daq
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from general import pi_data

STATS_INTERVAL = os.environ.get("STATS_INTERVAL", 5000)

logger = logging.getLogger()

layout = html.Div([
    dcc.Interval(
        id="general-stats-update",
        interval=int(STATS_INTERVAL),
        n_intervals=0,
    ),
    html.Div(
        className='row',
        children=[
            html.Div(
                className='four columns',
                children=[
                    html.H4("Raspberry Pi Stats:"),
                ]
            ),
            html.Div(
                className='eight columns',
                children=[
                    html.Div(
                        className='row',
                        children=[
                            html.Div(
                                [
                                    html.H6("CPU:"),
                                ],
                                className="four columns",  # general__stats__item",
                            ),
                            html.Div(
                                id="cpu-stats",
                                className="eight columns"  # general__stats__item",
                            ),
                        ]
                    ),
                    html.Div(
                        className='row',
                        children=[
                            html.Div(
                                [
                                    html.H6("RAM:"),
                                ],
                                className="four columns",  # general__stats__item",
                            ),
                            html.Div(
                                id="ram-stats",
                                className="eight columns"  # general__stats__item",
                            ),
                        ]
                    ),
                    html.Div(
                        className='row',
                        children=[
                            html.Div(
                                [
                                    html.H6("Disk:"),
                                ],
                                className="four columns",  # general__stats__item",
                            ),
                            html.Div(
                                id="disk-stats",
                                className="eight columns"  # general__stats__item",
                            ),
                        ]
                    ),
                ],
            ),
        ],
    ),
    html.Div(
        className='row',
        children=[
            html.Div(
                className='four columns',
                children=[
                    html.H4("Raspberry Pi Service Data:"),
                ]
            ),
            html.Div(
                className='eight columns',
                children=[
                    html.Div(
                        className='row',
                        children=[
                            html.Div(
                                className="four columns",
                                children=[
                                    html.H6("Dashboard:"),
                                ]
                            ),
                            html.Div(
                                id="dashbaord-states",
                                className="eight columns",
                            ),
                        ]
                    ),
                    html.Div(
                        className='row',
                        children=[
                            html.Div(
                                className="four columns",
                                children=[
                                    html.H6("MQTT Handler:"),
                                ]
                            ),
                            html.Div(
                                id="datalogger-states",
                                className="eight columns",
                            ),
                        ]
                    ),
                    html.Div(
                        className='row',
                        children=[
                            html.Div(
                                className="four columns",
                                children=[
                                    html.H6("Probemon:"),
                                ]
                            ),
                            html.Div(
                                id="mqtt-states",
                                className="eight columns",
                            ),
                        ]
                    ),
                ]
            ),
        ]
    )
])


def get_states(sub_color, active_color, load_color):
    return [
        html.Div(
            className='row',
            children=[
                html.Div(
                    className="one-third column",
                    children=[
                        daq.Indicator(
                            label="Service Running",
                            color=sub_color,
                            className="general__services__state",
                        ),
                    ]
                ),
                html.Div(
                    className="one-third column",
                    children=[
                        daq.Indicator(
                            label="Service State",
                            color=active_color,
                            className="general__services__state",
                        ),
                    ]
                ),
                html.Div(
                    className="one-third column",
                    children=[
                        daq.Indicator(
                            label="State Config File",
                            color=load_color,
                            className="general__services__state",
                        ),
                    ]
                ),
            ]
        )
    ]


def get_state_colors(data):
    if data:
        if data['LoadState'] == 'loaded':
            load_color = "green"
        elif data['LoadState'] == 'masked':
            load_color = "yellow"
        else:
            load_color = "red"

        if data['SubState'] == 'running':
            sub_color = "green"
        else:
            sub_color = "red"

        if data['ActiveState'] == 'active':
            active_color = "green"
        elif data['ActiveState'] in ['reloading', 'activating', 'deactivating']:
            active_color = "yellow"
        elif data['ActiveState'] == 'inactive':
            active_color = "orange"
        else:
            active_color = "red"
    else:
        load_color = "red"
        sub_color = "red"
        active_color = "red"
    return (sub_color, active_color, load_color)


@app.callback(Output('dashbaord-states', 'children'),
              [Input('general-stats-update', 'n_intervals')])
def update_dashboard_service(interval):
    data = pi_data.get_service_data("dashboard")
    colors = get_state_colors(data)
    return get_states(*colors)


@app.callback(Output('datalogger-states', 'children'),
              [Input('general-stats-update', 'n_intervals')])
def update_mqtt_handler_service(interval):
    data = pi_data.get_service_data("mqtthandler")
    colors = get_state_colors(data)
    return get_states(*colors)


@app.callback(Output('mqtt-states', 'children'),
              [Input('general-stats-update', 'n_intervals')])
def update_probemon_service(interval):
    data = pi_data.get_service_data("probemon", user=False)
    colors = get_state_colors(data)
    return get_states(*colors)


@app.callback(Output('cpu-stats', 'children'),
              [Input('general-stats-update', 'n_intervals')])
def cpu_state(interval):
    cpu_percent = pi_data.get_cpu_percent()
    return daq.GraduatedBar(
        max=100,
        value=cpu_percent,
        showCurrentValue=True,
        className='graduated__bar',
    )


@app.callback(Output('ram-stats', 'children'),
              [Input('general-stats-update', 'n_intervals')])
def ram_state(interval):
    ram = pi_data.get_ram_data()
    return daq.GraduatedBar(
        max=100,
        value=ram['percent'],
        showCurrentValue=True,
        className='graduated__bar',
    )


@app.callback(Output('disk-stats', 'children'),
              [Input('general-stats-update', 'n_intervals')])
def disk_state(interval):
    disk = pi_data.get_disk_data()
    return daq.GraduatedBar(
        max=100,
        value=disk['percent'],
        showCurrentValue=True,
        className='graduated__bar',
    )
