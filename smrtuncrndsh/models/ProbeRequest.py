#!/usr/bin/env python3

from . import db


class ProbeRequest(db.Model):
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

    def __repr__(self):
        return (
            "<ProbeRequest(id={self.id}, "
            f"date={self.date}, "
            f"macaddress={self.macaddress}, "
            f"make='{self.make}', "
            f"ssid='{self.ssid}', "
            f"rssi={self.rssi})>"
        )
