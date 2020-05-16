#!/usr/bin/env python3

from sqlalchemy import Column, Integer, DateTime, Float
from models.db import Base

class RoomData(Base):
    __tablename__ = 'temperature'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    temperature = Column(Float)
    humidity = Column(Float)
    pressure = Column(Float)
    brightness = Column(Float)
    altitude = Column(Float)

    def __repr__(self):
        return (
            "<RoomData("
            f"id={self.id}, "
            f"date={self.date}, "
            f"temperature={self.temperature}, "
            f"humidity='{self.humidity}', "
            f"pressure='{self.pressure}', "
            f"brightness={self.brightness}, "
            f"altitude={self.altitude})>"
        )
