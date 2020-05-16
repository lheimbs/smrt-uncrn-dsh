#!/usr/bin/env python3

from sqlalchemy import Column, Integer, DateTime, String
from models.db import ProbeBase

class ProbeRequest(ProbeBase):
    __tablename__ = 'probe-request'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    macaddress = Column(String)
    make = Column(String)
    ssid = Column(String)
    rssi = Column(Integer)

    def __repr__(self):
        return (
            "<ProbeRequest(id={self.id}, "
            f"date={self.date}, "
            f"macaddress={self.macaddress}, "
            f"make='{self.make}', "
            f"ssid='{self.ssid}', "
            f"rssi={self.rssi})>"
        )
