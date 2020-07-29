#!/usr/bin/env python3

from . import db, BaseMixin


class TabletBattery(db.Model, BaseMixin):
    __tablename__ = 'tablet_battery'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    level = db.Column(db.Integer)

    def to_dict(self):
        return {
            'date': self.date,
            'level': self.level,
        }

    def to_ajax(self):
        return {
            'edit': '',
            'delete': '',
            'id': self.id,
            'date': self.date,
            'level': self.level if self.level else '-',
        }

    def __repr__(self):
        return (
            "<TabletBattery("
            f"id={self.id}, "
            f"date={self.date}, "
            f"level={self.level})>"
        )
