#!/usr/bin/env python3
# coding=utf-8

import time
import logging
import socket
import json
import paho.mqtt.client as mqtt
from datetime import datetime

import mqtthandler.sql as sql
from mqtthandler.callbacks import (
    temp_message_to_db,
    handle_rf_transmission,
    handle_battery_level,
    handle_probes,
    handle_states,
    handle_tablet_charging
)

logger = logging.getLogger('mqtt_handler')
logger.debug('mqtthandler debug')
logger.info('mqtthandler info')
logger.warning('mqtthandler warning')
logger.error('mqtthandler error')


def connect(client):
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
    client = connect(client)

    try:
        while client:
            client.loop()
    except KeyboardInterrupt:
        logger.info("Script stopped through Keyboard Interrupt")
    finally:
        logger.info("Disconnecting client from broker.")
        client.disconnect()
