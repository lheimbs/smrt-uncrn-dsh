#!/usr/bin/env python3
# coding=utf-8

import time
import logging
import json
from datetime import datetime

import mqtthandler.sql as sql
from mqtthandler.detached import detachify

logger = logging.getLogger()

def temp_message_to_db(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    logger.debug(f"Add new RoomData reading into database: {payload}.")

    curr_time = datetime.now()
    room_data = json.loads(payload)
    if 'brightness' not in room_data.keys():
        room_data['brightness'] = 0

    sql.add_room_data_to_db(curr_time, **room_data)


def handle_rf_transmission(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    logger.debug(f"Add new RF transmission into database: {payload}.")

    curr_time = datetime.now()
    rf_data = json.loads(payload)
    rf_data['pulse_length'] = rf_data.pop('pulse-length')

    sql.add_rf_data_to_db(curr_time, **rf_data)


def handle_battery_level(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    logger.debug(f"Add new Tablet Battery info into database: {payload}.")
    curr_time = datetime.now()

    try:
        n_level = int(payload)
        logger.debug(f"Battery level detected: {n_level}")
        sql.add_tablet_battery_level(curr_time, n_level)
    except ValueError:
        n_level = 0
        logger.debug("Could not detect Battery level.")

    try:
        import rf_handler
        imported = True
    except ImportError:
        imported = False

    if imported:
        if 0 < n_level <= 20:
            logger.info("Battery low detected. Turn Socket on.")
            rf_handler.turn_socket_on(2, "rpi_rf")
        elif n_level >= 80:
            logger.info("Battery high detected. Turn socket off.")
            rf_handler.turn_socket_off(2, "rpi_rf")
    else:
        logger.info("Module 'rf_handler' is not avaliable. Skip battery handling.")


def handle_probes(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    logger.debug(f"Add new Probe Request into database: {payload}.")

    try:
        probe_request = json.loads(payload)
    except json.decoder.JSONDecodeError:
        logger.error("Badly formed payload could not get parsed by json-lib.")
        return

    probe_request['time'] = datetime.fromisoformat(probe_request['time'])
    sql.add_probe_request(**probe_request)


def handle_tablet_charging(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    curr_time = datetime.now()

    split_topic = msg.topic.replace('/charging', '').rsplit('/', 1)
    if len(split_topic) == 2:
        device = split_topic[1]

        logger.debug(f"Add new State into database: {device}: {payload}.")
        sql.add_state_to_db(curr_time, device, payload)
    else:
        logger.warning(f"Could not extract device name from topic. Aborting.")


def handle_states(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    curr_time = datetime.now()

    split_topic = msg.topic.replace('/status', '').rsplit('/', 1)
    if len(split_topic) == 2:
        device = split_topic[1]

        logger.debug(f"Add new State into database: {device}: {payload}.")
        sql.add_state_to_db(curr_time, device, payload)
    else:
        logger.warning(f"Could not extract device name from topic. Aborting.")


'''
def handle_room_control(client, userdata, msg):
    topic = msg.topic.replace("room/control/command/", '').replace("room/control/command", '')
    payload = msg.payload.decode("utf-8")
    logger.debug(f"New room command recieved: {msg.topic, payload}.")
    if (
        topic == "/socket"
        and socket_num.isdigit()
        and int(socket_num) in rf_handler.CODES.keys()
    ):
        if payload in ['on', '1']:
            logger.info("Socket command detected. Turn socket '{rf_handler.CODES[socket_num].name}' on.")
            rf_handler.turn_socket_on(int(socket_num), "rpi_rf")
        elif payload in ['off', '0']:
            logger.info("Socket command detected. Turn socket '{rf_handler.CODES[socket_num].name}' off.")
            rf_handler.turn_socket_off(int(socket_num), "rpi_rf")
        else:
            logger.warning("Socket command detected but invalid command '{payload}'. Available: ['on', 'off', 0, 1].")
    else:
        logger.info("No route for this command.")



@detachify
def handle_computer_state(payload):
    logger.debug(f"COMPUTER_STATUS={COMPUTER_STATUS}")
    if payload == 'on':
        if COMPUTER_STATUS == 'offline':
            logger.info("Turn computer on.")
            rf_handler.turn_socket_on(1, "rpi_rf")
            time.sleep(7)
            rf_handler.send_decimal(10000)
        else:
            logger.info("Computer is turned on. Doing nothing")
    else:
        logger.info("Turning computer off is currently unavaliable")
'''
