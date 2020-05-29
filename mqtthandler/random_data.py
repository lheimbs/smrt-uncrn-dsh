import random
import logging
from datetime import datetime

import paho.mqtt.publish as publish

logger = logging.getLogger('random_data_publisher')
alphabet = ['a', 'b', 'c', 'd', 'e', 'f']

def random_publish(choice, port):
    if choice == 'roomdata':
        logger.debug("Publish random room data.")
        publish.single(
            "room/data",
            (
                f'{{"temperature":{random.gauss(20,2)},'
                f'"humidity":{random.gauss(45,5)},'
                f'"pressure":{random.gauss(970,10)},'
                f'"altitude":{random.gauss(142.71, 1)},'
                '"brightness":0}'
            ),
            hostname="localhost",
            port=port,
        )
    elif choice == 'proberequest':
        logger.debug("Publish a random Probe Request.")
        publish.single(
            "mqtt/probes",
            (
                f'{{"time":"{datetime.now().isoformat()}",'
                f'"macaddress":"'
                f'{random.choice(alphabet)}{random.randrange(9)}:'
                f'{random.choice(alphabet)}{random.randrange(9)}:'
                f'{random.choice(alphabet)}{random.randrange(9)}:'
                f'{random.choice(alphabet)}{random.randrange(9)}",'
                '"make":"UNKNOWN",'
                '"ssid":"022696",'
                f'"rssi":{random.randint(-50, -10)}}}'
            ),
            hostname="localhost",
            port=port,
        )
    elif choice == 'battery':
        logger.debug("Publish random tablet battery.")
        publish.single(
            "tablet/shield/battery",
            random.randint(10, 90),
            hostname="localhost",
            port=port,
        )
    elif choice == 'rfdata':
        logger.debug("Publish random Rf-Data.")
        publish.single(
            "room/data/rf/recieve",
            '{"decimal":1131857,"length":24,"binary":"000100010100010101010001","pulse-length":315,"protocol":1}',
            hostname="localhost",
            port=port,
        )
    elif choice == 'state':
        devices = ['voice_assistant', 'esp_bme_rf', 'computer']
        device = random.choice(devices)

        logger.debug(f"Publish random State for device {device}.")
        publish.single(
            f"mqtt/{device}/status",
            random.choice(['online', 'offline']),
            hostname="localhost",
            port=port,
        )
    elif choice == 'charging':
        logger.debug("Publish random Tablet Charging State.")
        publish.single(
            "tablet/shield/charging",
            random.choice(['charging', 'discharging']),
            hostname="localhost",
            port=port,
        )

    return random.choice(['rfdata', 'battery', 'proberequest', 'roomdata', 'state', 'charging'])
