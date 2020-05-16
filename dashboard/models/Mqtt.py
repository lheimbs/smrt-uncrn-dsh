#!/usr/bin/env python3

from sqlalchemy import Column, Integer, DateTime, String, Boolean
from models.db import Base

class Mqtt(Base):
    __tablename__ = 'mqtt-message'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    topic = Column(String)
    payload = Column(String)
    qos = Column(Integer)
    retain = Column(Boolean)

    def __repr__(self):
        return (
            "<Mqtt(id={self.id}, "
            f"date={self.date}, "
            f"topic={self.topic}, "
            f"payload='{self.payload}', "
            f"qos='{self.qos}', "
            f"retain={self.retain})>"
        )
