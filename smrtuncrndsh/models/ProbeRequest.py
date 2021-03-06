#!/usr/bin/env python3

from . import db, BaseMixin


class ProbeRequest(db.Model, BaseMixin):
    __tablename__ = 'probe_requests'
    __bind_key__ = 'probe_request'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    macaddress = db.Column(db.String)
    make = db.Column(db.String)
    ssid = db.Column(db.String)
    rssi = db.Column(db.Integer)

    def to_dict(self):
        return {
            'date': self.date,
            'macaddress': self.macaddress,
            'make': self.make,
            'ssid': self.ssid,
            'rssi': self.rssi,
        }

    def to_ajax(self):
        return {
            'edit': '',
            'delete': '',
            'id': self.id,
            'date': self.date,
            'macaddress': self.macaddress if self.macaddress else '-',
            'make': self.make if self.make else '-',
            'ssid': self.ssid if self.ssid else '-',
            'rssi': self.rssi if self.rssi else '-',
        }

    def __repr__(self):
        return (
            "<ProbeRequest(id={self.id}, "
            f"date={self.date}, "
            f"macaddress={self.macaddress}, "
            f"make='{self.make}', "
            f"ssid='{self.ssid}', "
            f"rssi={self.rssi})>"
        )
