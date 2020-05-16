#!/usr/bin/env python3

import logging
import socket
import unicodedata
from datetime import datetime
from collections import deque

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import paho.mqtt.client as mqtt
from dash.dependencies import Input, Output

from app import app, COLORS

logger = logging.getLogger()

MQTT_CLIENT = mqtt.Client("Dashboard")
MQTT_CLIENT.connected_flag = False
MQTT_CLIENT.enable_logger()
QUEUE = deque(maxlen=20)

def mqtt_connect(client):
    brokers = ['localhost', 'lennyspi.local', '192.168.1.201', '192.168.1.205']
    port = 8883
    for host in brokers:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logger.debug(f"Try connection to broker {host} on port {port}.")
        if sock.connect_ex((host, port)) == 0:
            try:
                client.connect(host, port, 60)
                logger.info(f"Connected to broker on host {host}.")
                break
            except ConnectionRefusedError:
                logger.warning("Broker refused connection. Are host/port correct?")
            except socket.gaierror:
                logger.warning("Connection to broker failed. Hostname is probably not valid.")
            except TimeoutError:
                logger.warning("Connecting to broker timed out.")
    else:
        logger.error("Could not connect to broker.")
        return None
    return client


def sanitize_topic(topic):
    allowed_cats = ('Ll', 'Lu', 'Lo', 'Nd')
    allowed_chars = ('SOLIDUS', 'HYPHEN-MINUS', 'NUMBER SIGN')

    if not topic:
        return False

    for curr_char in topic:
        cat = unicodedata.category(curr_char)
        if cat in allowed_cats:
            continue

        name = unicodedata.name(curr_char)
        if name in allowed_chars:
            continue

        # character is not whitelisted
        return False
    # all characters are whitelisted
    return True


def mqtt_connect_async(client, queue):
    def on_connect(client, userdata, flags, rc):
        client.connected_flag = True
        logger.debug("'on_connect' called.")

    def on_message(client, userdata, msg):
        logger.debug("'on_message' called")
        now = datetime.now()
        queue.append(
            {
                'date': now.strftime('%d.%m.%Y'),
                'time': now.strftime('%X'),
                'topic': msg.topic,
                'payload': msg.payload.decode('UTF-8'),
                'qos': msg.qos,
            }
        )

    def on_disconnect(client, userdata, rc):
        client.connected_flag = False
        if rc != 0:
            logger.debug("Unexpected disconnection.")

    client.on_connect = on_connect
    client.on_message = on_message

    client = mqtt_connect(client)
    if client:
        client.loop_start()


if MQTT_CLIENT.connected_flag:
    layout = html.Div(
        className='row',
        children=[
            html.Div(
                className='two columns settings',
                children=[
                    html.Datalist(
                        id='mqtt-topic-recent',
                        children=[html.Option(value=val) for val in sql_data.get_mqtt_topics()],
                    ),
                    dcc.Input(
                        id='mqtt-topic-input',
                        list='mqtt-topic-recent',
                        placeholder="Topic...",
                        style={
                            'backgroundColor': COLORS['background-medium'],
                            'color': COLORS['foreground'],
                            'border': f"2px solid {COLORS['foreground']}",
                            'border-radius': '4px',
                            'padding': '6px 10px',
                        },
                    ),
                    html.Button('Subscribe', id='mqtt-live-subscribe'),
                    html.Hr(),
                    html.Button(
                        'Start',
                        id='mqtt-live-start',
                        disabled=False,
                        className='start__stop__button',
                    ),
                    html.Button('Stop', id='mqtt-live-stop', disabled=True, className='start__stop__button'),
                    html.Hr(),
                    html.Div(id='mqtt-live-sub-status'),
                ],
            ),
            html.Div(
                className='ten columns settings',
                children=[
                    dcc.Interval(id='mqtt-live-interval', interval=500),
                    dash_table.DataTable(
                        id='live-table',
                        columns=[
                            {"name": 'Date', "id": 'date'},
                            {"name": 'Time', "id": 'time'},
                            {"name": 'Topic', "id": 'topic'},
                            {"name": 'Quality of Service', "id": 'qos'},
                            {"name": 'Payload', "id": 'payload'},
                        ],
                        data=[],
                        editable=False,
                        fill_width=False,
                        page_action="native",
                        page_current=0,
                        page_size=20,
                        style_as_list_view=True,
                        is_focused=False,
                        style_header={
                            'backgroundColor': COLORS['background-medium'],
                            'fontWeight': 'bold'
                        },
                        style_cell={
                            'padding': '5px',
                            'textAlign': 'center',
                            'backgroundColor': COLORS['background'],
                        },
                        style_cell_conditional=[
                            {
                                'if': {'column_id': 'payload'},
                                'textAlign': 'left'
                            }
                        ],
                        style_data={
                            'whiteSpace': 'normal',
                            'height': 'auto'
                        },
                        style_data_conditional=[
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': COLORS['background-medium']
                            }
                        ],
                    ),
                ],
            ),
        ],
    )
else:
    layout = "Live mqtt data not avaliable!"


@app.callback(Output('mqtt-topic-input', 'style'),
              [Input('mqtt-topic-input', 'value')])
def mqtt_live_sanitize_topic(topic):
    if topic:
        if sanitize_topic(topic):
            style = {
                'backgroundColor': COLORS['background-medium'],
                'color': COLORS['foreground'],
                'border': f"2px solid {COLORS['green']}",
                'border-radius': '4px',
                'padding': '6px 10px',
            }
        else:
            style = {
                'backgroundColor': COLORS['background-medium'],
                'color': COLORS['foreground'],
                'border': f"2px solid {COLORS['red']}",
                'border-radius': '4px',
                'padding': '6px 10px',
            }
    else:
        style = {
            'backgroundColor': COLORS['background-medium'],
            'color': COLORS['foreground'],
            'border': f"2px solid {COLORS['foreground']}",
            'border-radius': '4px',
            'padding': '6px 10px',
        }
    return style


@app.callback(Output('mqtt-live-sub-status', 'children'),
              [Input('mqtt-live-subscribe', 'n_clicks'),
               Input('mqtt-topic-input', 'value')])
def subscribe_mqtt_topic(n_clicks, topic):
    global MQTT_CLIENT, N_BUTTON_HIST

    ctx = dash.callback_context
    if not ctx.triggered or not topic or not n_clicks or N_BUTTON_HIST == n_clicks:
        return ""
    elif not sanitize_topic(topic):
        N_BUTTON_HIST = n_clicks
        return "Invalid Topic!"
    elif not MQTT_CLIENT.connected_flag:
        N_BUTTON_HIST = n_clicks
        return "Press Start first!"
    else:
        N_BUTTON_HIST = n_clicks
        MQTT_CLIENT.subscribe(topic)
        return "Subscribed!"


@app.callback([Output('mqtt-live-start', 'disabled'),
               Output('mqtt-live-stop', 'disabled')],
              [Input('mqtt-live-start', 'n_clicks'),
               Input('mqtt-live-stop', 'n_clicks')])
def toggle_buttons(n_clicksb1, n_clicksb2):
    global MQTT_CLIENT
    if dash.callback_context.triggered:
        context = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
        if context == 'mqtt-live-start':
            mqtt_connect_async(MQTT_CLIENT, QUEUE)
            return True, False
        else:
            MQTT_CLIENT.disconnect()
            MQTT_CLIENT = mqtt.Client("Dashboard")
            MQTT_CLIENT.connected_flag = False
            MQTT_CLIENT.enable_logger()
            return False, True
    return True, False


@app.callback(Output('live-table', 'data'),
              [Input('mqtt-live-interval', 'n_intervals')])
def render_mqtt_live(interval):
    return list(QUEUE)
