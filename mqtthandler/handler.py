#!/usr/bin/env python3
# coding=utf-8

import time
import logging
import socket
import subprocess
import random
import paho.mqtt.client as mqtt
from datetime import datetime

from mqtthandler.PipeLogging import LogPipe
from mqtthandler.random_data import random_publish
import mqtthandler.sql as sql

from mqtthandler.callbacks import (
    temp_message_to_db,
    handle_rf_transmission,
    handle_battery_level,
    handle_probes,
    handle_states,
    handle_tablet_charging
)

import sys
sys.path.insert(0, '..')
from dashboard.app import server            # noqa E402

logger = logging.getLogger('mqtt_handler')


def connect(client, brokers=None, port=None):
    if not brokers:
        brokers = ['localhost', 'lennyspi.local', '192.168.1.201', '192.168.1.205']
    if not port:
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


def on_connect(client, userdata, flags, rc):
    topic = '#'
    client.subscribe(topic)
    logger.info(f"Subscribed to topic '{topic}'.")


def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode("utf-8")

    logger.debug(f"'on_message' called: topic='{topic}', msg='{payload}'.")

    if topic == 'trash':
        logger.info("Message is trash. Discarding")
    else:
        sql.add_mqtt_to_db(datetime.now(), topic, payload, msg.qos, msg.retain)


def main():
    client = mqtt.Client()
    broker = None

    mqtt_logger = logging.getLogger('client')
    mqtt_logger.setLevel(logging.INFO)
    client.enable_logger(logger=mqtt_logger)

    client.on_connect = on_connect
    client.on_message = on_message

    client.message_callback_add("room/data", temp_message_to_db)
    client.message_callback_add("room/data/rf/recieve", handle_rf_transmission)
    client.message_callback_add("tablet/shield/battery", handle_battery_level)
    client.message_callback_add("tablet/shield/charging", handle_tablet_charging)
    client.message_callback_add("mqtt/probes", handle_probes)
    client.message_callback_add("mqtt/computer/status", handle_states)
    client.message_callback_add("mqtt/esp_bme_rf/status", handle_states)
    client.message_callback_add("mqtt/voice_assistant/status", handle_states)

    # connect to broker
    if server.config['DEBUG']:
        logger.info(f"Using development broker: {server.config['MQTT_SERVER']}.")

        sys.stdout = LogPipe(logging.DEBUG, 'local_broker')
        sys.stderr = LogPipe(logging.INFO, 'local_broker')

        broker = subprocess.Popen(
            ['mosquitto', '-p', str(server.config['MQTT_PORT'])],
            stdout=sys.stdout,
            stderr=sys.stderr
        )
        logger.debug(f"Starting development broker locally. PID: {broker.pid}.")
        time.sleep(1)

        client = connect(client, (server.config['MQTT_SERVER'],), server.config['MQTT_PORT'])
    else:
        client = connect(client)

    try:
        if server.config['DEBUG']:
            start_time = time.time()
            rand_time = random.randint(3, 9)
            choice = 'roomdata'
            client.loop_start()

        while client:
            if server.config['DEBUG']:
                if time.time() % rand_time == 0:
                    choice = random_publish(choice, server.config['MQTT_PORT'])
                    rand_time = random.randint(10, 90)
                elif time.time() - start_time >= 60:
                    random_publish('roomdata', server.config['MQTT_PORT'])
                    start_time = time.time()
            else:
                client.loop()

    except KeyboardInterrupt:
        logger.info("Script stopped through Keyboard Interrupt")
        if server.config['DEBUG']:
            client.loop_stop()
    finally:
        logger.info("Disconnecting client from broker.")
        if client and client.is_connected:
            client.disconnect()
        if broker:
            # close the file handlers properly
            sys.stdout.close()
            sys.stdout = sys.__stdout__
            sys.stderr.close()
            sys.stderr = sys.__stderr__
            broker.terminate()
