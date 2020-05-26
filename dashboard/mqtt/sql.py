#!/usr/bin/env python3

import logging
import pandas as pd

from ..app import db
from ..models.Mqtt import Mqtt

logger = logging.getLogger()

def get_mqtt_topics_as_options():
    topics = []
    for topic in db.session.query(Mqtt.topic).distinct().order_by(Mqtt.topic):
        topics.append({'label': topic.topic, 'value': topic.topic})
    return topics


def get_mqtt_messages_by_topic(topics, limit):
    messages_dict = []
    messages = Mqtt.query.filter(Mqtt.topic.in_(topics)).order_by(Mqtt.date.desc()).limit(limit)
    for message in messages:
        message = message.to_dict()
        message.update({'time': message['date'].time()})
        message['date'] = message['date'].date()
        messages_dict.append(message)
    return pd.DataFrame(messages_dict, columns=['date', 'time', 'topic', 'payload', 'retain', 'qos'])
