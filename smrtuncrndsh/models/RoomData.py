#!/usr/bin/env python3

from . import db, BaseMixin


class RoomData(db.Model, BaseMixin):
    __tablename__ = 'room_data'

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

    def to_ajax(self):
        return {
            'edit': '',
            'delete': '',
            'id': self.id,
            'date': self.date,
            'temperature': f"{self.temperature:.2f}" if self.temperature else '-',
            'humidity': self.humidity if self.humidity else '-',
            'pressure': self.pressure if self.pressure else '-',
            'brightness': self.brightness if self.brightness else '-',
            'altitude': f"{self.altitude:.2f}" if self.altitude else '-',
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
