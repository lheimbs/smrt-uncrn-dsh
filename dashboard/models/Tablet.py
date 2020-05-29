#!/usr/bin/env python3

from app import db

class TabletBattery(db.Model):
    __tablename__ = 'tablet-battery'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    level = db.Column(db.Integer)

    def to_dict(self):
        return {
            'date': self.date,
            'level': self.battery,
        }

    def __repr__(self):
        return (
            "<TabletBattery("
            f"id={self.id}, "
            f"date={self.date}, "
            f"level={self.battery})>"
        )