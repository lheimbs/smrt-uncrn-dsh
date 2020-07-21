#!/usr/bin/env python3

from . import db, BaseMixin


class Mqtt(db.Model, BaseMixin):
    __tablename__ = 'mqtt_messages'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    topic = db.Column(db.String)
    payload = db.Column(db.String)
    qos = db.Column(db.Integer)
    retain = db.Column(db.Boolean)

    def to_dict(self):
        return {
            'date': self.date,
            'topic': self.topic,
            'payload': self.payload,
            'qos': self.qos,
            'retain': self.retain,
        }

    def to_ajax(self):
        return {
            'edit': '',
            'delete': '',
            'id': self.id,
            'date': self.date,
            'topic': self.topic if self.topic else '-',
            'payload': self.payload if self.payload else '-',
            'qos': self.qos if self.qos else '-',
            'retain': self.retain if self.retain else '-',
        }

    def __repr__(self):
        return (
            "<Mqtt(id={self.id}, "
            f"date={self.date}, "
            f"topic={self.topic}, "
            f"payload='{self.payload}', "
            f"qos='{self.qos}', "
            f"retain={self.retain})>"
        )
