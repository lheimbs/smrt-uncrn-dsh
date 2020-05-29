#!/usr/bin/env python3

# from sqlalchemy import Column, Integer, DateTime, Float
# from models.db import Base
from dashboard.app import db

class RoomData(db.Model):
    __tablename__ = 'room-data'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    pressure = db.Column(db.Float)
    brightness = db.Column(db.Float)
    altitude = db.Column(db.Float)

    def to_dict(self):
        return {
            'date': self.date,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'pressure': self.pressure,
            'brightness': self.brightness,
            'altitude': self.altitude,
        }

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
